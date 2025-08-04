import time
import logging
from app.timer import TimerController
from app.display import Display
from app.input import ButtonInput, JoystickInput
from app.output import Output

logger = logging.getLogger(__name__)

def get_version():
    try:
        from app.version import __version__
        return __version__
    except Exception:
        return "unknown"

def get_text_size(draw, text, font):
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    return draw.textsize(text, font=font)

def show_version_splash(display, version=None):
    from PIL import ImageDraw, ImageFont, Image
    img = Image.new('1', (display.width, display.height), 0)
    draw = ImageDraw.Draw(img)
    if version is None:
        version = get_version()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    lines = ["Simple Timer", f"{version}"]
    text_h = sum(get_text_size(draw, line, font)[1] for line in lines)
    y = (display.height - text_h) // 2
    for line in lines:
        w, h = get_text_size(draw, line, font)
        x = (display.width - w) // 2
        draw.text((x, y), line, font=font, fill=255)
        y += h
    display.hw.Init()
    display.hw.clear()
    display.ShowImage(display.getbuffer(img))
    time.sleep(1.5)
    display.hw.clear()

class AppController:
    def __init__(self, debug: bool = False, display_hardware=None):
        self.debug = debug
        self.display = Display(hardware=display_hardware) if display_hardware else Display()
        show_version_splash(self.display)
        self.timer = TimerController()
        self.buttons = ButtonInput()
        self.joystick = JoystickInput()
        self.output = Output()
        self.running = True
        self.selected_timer = None
        self.key2_was_pressed = False
        self.key2_press_time = None

        self._last_output_status = self.timer.status
        self._last_timer_enabled = self.timer.enabled
        self._last_timer_status = self.timer.status
        self._last_timer_mode = self.timer.mode
        self._last_timer_elapsed = self.timer.elapsed

        self._clock_symbols = ["|", "/", "-", "\\"]
        self._clock_index = 0
        self._last_anim_time = time.monotonic()
        self._pause_spin = False

        self._init_display()
        self._check_mock_display()

        self.timer.status_a = ""
        self.timer.status_b = ""
        self.timer.status_c = self.timer.mode

        self._refresh_display()

    def _init_display(self):
        self.display.hw.Init()
        self.display.hw.clear()

    def _check_mock_display(self):
        if hasattr(self.display, "_is_mock") and self.display._is_mock():
            logger.info("Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

    def _refresh_display(self):
        self.display.update_values(self.timer)
        self.display.ShowImage(self.display.getbuffer(self.display.image))

    def _toggle_selection(self, timer_type):
        self.selected_timer = None if self.selected_timer == timer_type else timer_type

    def _exit_selection(self):
        self.selected_timer = None

    def _joystick_adjust(self, direction):
        if self.selected_timer in ("OPEN", "CLOSE"):
            self._adjust_time_base(self.selected_timer, direction)
            self.timer.save_settings()
        elif self.selected_timer == "MODE":
            self.timer.handle_mode_adjustment(direction)

    def _adjust_time_base(self, timer_type, direction):
        if timer_type == "OPEN":
            self._set_time_base("_open_time_base", direction, "OPEN")
        elif timer_type == "CLOSE":
            self._set_time_base("_close_time_base", direction, "CLOSE")

    def _set_time_base(self, attr, direction, label):
        old_value = getattr(self.timer, attr)
        new_value = max(1, old_value + direction)
        setattr(self.timer, attr, new_value)
        self.timer.randomize_if_needed()
        logger.info(
            "%s %s base time to %d",
            "Increased" if direction > 0 else "Decreased",
            label,
            new_value
        )

    def _cycle_timer_mode(self, direction):
        self.timer.cycle_mode(direction)
        logger.info(f"Switched to {self.timer.mode} mode")

    def _toggle_pause_resume(self):
        self.timer.enabled = not self.timer.enabled
        if self.timer.enabled:
            self.timer.last_update_time = time.monotonic()
            logger.info("Timer resumed (short press).")
            self._pause_spin = False
        else:
            logger.info("Timer paused (short press).")
            self._pause_spin = True

    def _reset_and_reload(self):
        self._reset_timer_common()
        self.timer.load_settings()
        self.timer.status = "OPEN"
        self._update_output()

    def _full_reset(self):
        self._reset_timer_common()
        self.timer.reset_settings()
        self.timer.status = "OPEN"
        self._update_output()

    def _reset_timer_common(self):
        self.timer.enabled = False
        self.timer.elapsed = 0
        self.timer.show_zero = False
        self._pause_spin = True

    def log_timer_state_changes(self):
        self._log_state_change('enabled', self.timer.enabled, '_last_timer_enabled')
        self._log_state_change('status', self.timer.status, '_last_timer_status')
        self._log_state_change('mode', self.timer.mode, '_last_timer_mode')
        if int(self.timer.elapsed) != int(self._last_timer_elapsed):
            logger.debug(f"Timer elapsed changed: {int(self._last_timer_elapsed)} -> {int(self.timer.elapsed)}")
            self._last_timer_elapsed = self.timer.elapsed

    def _log_state_change(self, name, current_value, last_attr):
        last_value = getattr(self, last_attr)
        if current_value != last_value:
            logger.debug(f"Timer {name} changed: {last_value} -> {current_value}")
            setattr(self, last_attr, current_value)

    def run(self):
        try:
            while self.running:
                self.handle_buttons()
                self._update_timer_and_display()
                self.log_timer_state_changes()
                time.sleep(0.1)
        finally:
            self._cleanup()

    def _update_timer_and_display(self):
        now = time.monotonic()
        if self.timer.enabled:
            self.timer.update()
            self._update_output()
            if now - self._last_anim_time > 0.2:
                self._clock_index = (self._clock_index + 1) % len(self._clock_symbols)
                self._last_anim_time = now
        self.timer.status_a = self._clock_symbols[self._clock_index]
        self.timer.status_b = self.timer.get_status_b()
        self._refresh_display()

    def _update_output(self):
        if self.timer.status != self._last_output_status:
            self.output.set_state(1, self.timer.status == "CLOSE")
            self._last_output_status = self.timer.status

    def _cleanup(self):
        self.buttons.cleanup()
        self.joystick.cleanup()
        self.output.cleanup()
        if hasattr(self.display, "hw") and hasattr(self.display.hw, "RPI"):
            try:
                self.display.hw.RPI.module_exit()
                logger.info("GPIO cleanup done.")
            except Exception as e:
                logger.error("GPIO cleanup failed: %s", e)

    # --- Unified input handling ---

    def handle_buttons(self):
        # KEY2: pause/resume or reset/full reset
        if self.buttons.is_pressed('KEY2'):
            if not self.key2_was_pressed:
                self.key2_press_time = time.monotonic()
                self.key2_was_pressed = True
        else:
            if self.key2_was_pressed:
                if self.key2_press_time is not None:
                    duration = time.monotonic() - self.key2_press_time
                    if duration >= 5.0:
                        self._full_reset()
                        logger.info("Timer stopped and FULLY reset (key2 held ≥5s).")
                    elif duration >= 2.0:
                        self._reset_and_reload()
                        logger.info("Timer stopped and reloaded from settings (key2 held ≥2s).")
                    else:
                        self._toggle_pause_resume()
                self.key2_press_time = None
                self.key2_was_pressed = False

        # KEY1/KEY3: select/deselect CLOSE/OPEN
        if self.buttons.is_pressed('KEY1'):
            self._toggle_selection("CLOSE")
        if self.buttons.is_pressed('KEY3'):
            self._toggle_selection("OPEN")

        # Joystick press: select/deselect MODE
        if self.joystick.is_active('press'):
            self._toggle_selection("MODE")

        # KEY2 or joystick left/right: exit selection
        if self.selected_timer and self.buttons.is_pressed('KEY2'):
            self._exit_selection()
        elif self.selected_timer == "MODE" and (self.joystick.is_active('left') or self.joystick.is_active('right')):
            self._exit_selection()

        # Joystick up/down: adjust selected timer/mode
        if self.joystick.is_active('up'):
            self._joystick_adjust(1)
            time.sleep(0.2)
        elif self.joystick.is_active('down'):
            self._joystick_adjust(-1)
            time.sleep(0.2)

        # Joystick left/right: cycle mode
        if self.joystick.is_active('left'):
            self._exit_selection()
            self._cycle_timer_mode(-1)
            self.timer.status_c = self.timer.mode
            time.sleep(0.2)
        elif self.joystick.is_active('right'):
            self._exit_selection()
            self._cycle_timer_mode(1)
            self.timer.status_c = self.timer.mode
            time.sleep(0.2)

        self._refresh_display()

    # --- API handlers for web/remote control ---

    def handle_key(self, key_name):
        if key_name == "KEY2":
            self._toggle_pause_resume()
            self._exit_selection()
        elif key_name == "KEY1":
            self._toggle_selection("CLOSE")
        elif key_name == "KEY3":
            self._toggle_selection("OPEN")
        self._refresh_display()

    def handle_joystick(self, direction):
        if direction == "up":
            self._joystick_adjust(1)
        elif direction == "down":
            self._joystick_adjust(-1)
        elif direction == "left":
            self._exit_selection()
            self._cycle_timer_mode(-1)
            self.timer.status_c = self.timer.mode
        elif direction == "right":
            self._exit_selection()
            self._cycle_timer_mode(1)
            self.timer.status_c = self.timer.mode
        elif direction == "press":
            self._toggle_selection("MODE")
        self._refresh_display()