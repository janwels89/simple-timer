import time
import logging
from app.timer import TimerController
from app.display import Display
from app.input import ButtonInput, JoystickInput
from app.output import Output  # <-- Added for output integration

logger = logging.getLogger(__name__)

def get_version():
    try:
        from app.version import __version__
        return __version__
    except Exception:
        return "unknown"

def get_text_size(draw, text, font):
    # Pillow >=10: use textbbox, else fallback to textsize
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    return draw.textsize(text, font=font)

def show_version_splash(display, version=None):
    from PIL import ImageDraw, ImageFont, Image
    import time

    img = Image.new('1', (display.width, display.height), 0)  # 0 = black background
    draw = ImageDraw.Draw(img)

    if version is None:
        version = get_version()

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    lines = [
        "Simple Timer",
        f"{version}"
    ]
    text_h = sum([get_text_size(draw, line, font)[1] for line in lines])
    y = (display.height - text_h) // 2

    for line in lines:
        w, h = get_text_size(draw, line, font)
        x = (display.width - w) // 2
        draw.text((x, y), line, font=font, fill=255)  # 255=white
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
        self.output = Output()  # <-- Instantiate Output for controlling GPIOs
        self._last_output_status = self.timer.status  # <-- Track last output status
        self.running = True
        self.selected_timer = None
        self.key2_was_pressed = False
        self.key2_press_time = None

        # For state change logging
        self._last_timer_enabled = self.timer.enabled
        self._last_timer_status = self.timer.status
        self._last_timer_mode = self.timer.mode
        self._last_timer_elapsed = self.timer.elapsed

        # Spinner for status_a
        self._clock_symbols = ["|", "/", "-", "\\"]
        self._clock_index = 0
        self._last_anim_time = time.monotonic()
        self._pause_spin = False

        # Only clear/init the display now, splash is shown already
        self._init_display()
        self._check_mock_display()

        self.timer.status_a = ""
        self.timer.status_b = ""
        self.timer.status_c = self.timer.mode

        self._draw_layout()

    def _init_display(self):
        self.display.hw.Init()
        self.display.hw.clear()

    def _check_mock_display(self):
        if hasattr(self.display, "_is_mock") and self.display._is_mock():
            logger.info("Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

    def _draw_layout(self):
        self.display.draw_layout(
            self.timer.open_time,
            self.timer.close_time,
            self.timer.status_a,
            self.timer.status_b,
            self.timer.status_c,
            open_base=self.timer._open_time_base,
            close_base=self.timer._close_time_base
        )
        self.display.ShowImage(self.display.getbuffer(self.display.image))

    def handle_buttons(self):
        self._handle_key2_press()
        self._handle_select_press('KEY3', 'OPEN')
        self._handle_select_press('KEY1', 'CLOSE')
        self._handle_mode_select_press()  # NEW: joystick press for mode select/deselect
        self._handle_selection_exit()
        self._handle_joystick_adjust()
        self._handle_joystick_mode_cycle()

    def _handle_key2_press(self):
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

    def _handle_select_press(self, key, timer_type):
        if self.buttons.is_pressed(key):
            if self.selected_timer == timer_type:
                logger.info(f"Exited selection mode for {timer_type} ({key} pressed again).")
                self.selected_timer = None
            else:
                self.selected_timer = timer_type
                logger.info(f"Selected {timer_type} timer for editing.")

    def _handle_mode_select_press(self):
        # Joystick "press" (center click) selects MODE, and deselects OPEN/CLOSE if selected
        if self.joystick.is_active('press'):  # FIXED: use is_active, not is_pressed
            if self.selected_timer == "MODE":
                logger.info("Exited MODE selection (joystick pressed again)")
                self.selected_timer = None
            else:
                if self.selected_timer in ("OPEN", "CLOSE"):
                    logger.info(f"Switching from {self.selected_timer} selection to MODE (joystick press)")
                else:
                    logger.info("Selected MODE for editing (joystick press)")
                self.selected_timer = "MODE"

    def _handle_selection_exit(self):
        # KEY2 always exits any selection
        if self.selected_timer and self.buttons.is_pressed('KEY2'):
            logger.info(f"Exited selection mode for {self.selected_timer} (KEY2).")
            self.selected_timer = None
        # Joystick left/right also exits MODE selection (for consistency)
        elif self.selected_timer == "MODE" and (self.joystick.is_active('left') or self.joystick.is_active('right')):
            logger.info(f"Exited selection mode for MODE (joystick left/right).")
            self.selected_timer = None

    def _handle_joystick_adjust(self):
        direction = 0
        if self.joystick.is_active('up'):
            direction = 1
        elif self.joystick.is_active('down'):
            direction = -1

        if direction == 0:
            return

        if self.selected_timer == "OPEN":
            self._adjust_time_base("OPEN", direction)
            self.timer.save_settings()
            time.sleep(0.2)  # Debounce
        elif self.selected_timer == "CLOSE":
            self._adjust_time_base("CLOSE", direction)
            self.timer.save_settings()
            time.sleep(0.2)  # Debounce
        elif self.selected_timer == "MODE":
            self.timer.handle_mode_adjustment(direction)
            time.sleep(0.2)
        else:
            # No selection: do nothing or default (optional)
            pass

    def _adjust_time_base(self, timer_type, direction):
        if timer_type == "OPEN":
            self.timer._open_time_base = max(1, self.timer._open_time_base + direction)
            self.timer.randomize_if_needed()
            logger.info(
                "%s OPEN base time to %d",
                "Increased" if direction > 0 else "Decreased",
                self.timer._open_time_base
            )
        elif timer_type == "CLOSE":
            self.timer._close_time_base = max(1, self.timer._close_time_base + direction)
            self.timer.randomize_if_needed()
            logger.info(
                "%s CLOSE base time to %d",
                "Increased" if direction > 0 else "Decreased",
                self.timer._close_time_base
            )

    def _handle_joystick_mode_cycle(self):
        left = self.joystick.is_active('left')
        right = self.joystick.is_active('right')
        if left or right:
            if self.selected_timer:
                logger.info(f"Exited selection mode for {self.selected_timer} (joystick {'left' if left else 'right'}).")
                self.selected_timer = None
            # Always cycle mode after exiting timer selection (or if none selected)
            self._cycle_timer_mode(-1 if left else 1)
            self.timer.status_c = self.timer.mode
            self._draw_layout()
            time.sleep(0.2)  # Debounce

    def _cycle_timer_mode(self, direction):
        # Delegate mode cycling to timer controller
        self.timer.cycle_mode(direction)
        logger.info(f"Switched to {self.timer.mode} mode")

    def _toggle_pause_resume(self):
        self.timer.enabled = not self.timer.enabled
        if self.timer.enabled:
            self.timer.last_update_time = time.monotonic()
            logger.info("Timer resumed (short press).")
            self._pause_spin = False  # Resume spinning
        else:
            logger.info("Timer paused (short press).")
            self._pause_spin = True   # Pause spinning, but keep spinner visible

    def _reset_and_reload(self):
        self.timer.enabled = False
        self.timer.elapsed = 0
        self.timer.show_zero = False
        self.timer.status = "OPEN"
        self.timer.load_settings()
        self._pause_spin = True  # Keep spinner visible and paused

    def _full_reset(self):
        self.timer.enabled = False
        self.timer.elapsed = 0
        self.timer.show_zero = False
        self.timer.status = "OPEN"
        self.timer.reset_settings()
        self._pause_spin = True  # Keep spinner visible and paused

    def log_timer_state_changes(self):
        self._log_state_change('enabled', self.timer.enabled, '_last_timer_enabled')
        self._log_state_change('status', self.timer.status, '_last_timer_status')
        self._log_state_change('mode', self.timer.mode, '_last_timer_mode')
        # Only log elapsed if integer value changes
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
            self._update_output()  # <-- Call output update on timer update
            # Animate spinner for status_a
            if now - self._last_anim_time > 0.2:
                self._clock_index = (self._clock_index + 1) % len(self._clock_symbols)
                self._last_anim_time = now
            self.timer.status_a = self._clock_symbols[self._clock_index]
        else:
            # When paused, keep spinner symbol, but do not advance
            self.timer.status_a = self._clock_symbols[self._clock_index]

        # Ask timer for status_b (mode-specific display)
        self.timer.status_b = self.timer.get_status_b()

        self.display.update_values(self.timer)
        self.display.ShowImage(self.display.getbuffer(self.display.image))

    def _update_output(self):
        """Set GPIO output based on timer status, only when it changes."""
        if self.timer.status != self._last_output_status:
            if self.timer.status == "CLOSE":
                self.output.set_state(1, True)   # Relay ON (GPIO4 LOW)
            else:
                self.output.set_state(1, False)  # Relay OFF (GPIO4 HIGH)
            self._last_output_status = self.timer.status

    def _cleanup(self):
        self.buttons.cleanup()
        self.joystick.cleanup()
        self.output.cleanup()  # <-- Ensure GPIO cleanup on exit
        if hasattr(self.display, "hw") and hasattr(self.display.hw, "RPI"):
            try:
                self.display.hw.RPI.module_exit()
                logger.info("GPIO cleanup done.")
            except Exception as e:
                logger.error("GPIO cleanup failed: %s", e)