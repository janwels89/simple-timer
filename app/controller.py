import time
import logging
from app.timer import TimerController
from app.display import Display
from app.input import ButtonInput, JoystickInput

logger = logging.getLogger(__name__)

class AppController:
    def __init__(self, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.display = Display()
        self.timer = TimerController()
        self.buttons = ButtonInput()
        self.joystick = JoystickInput()
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

        # Display initialization
        self.display.hw.Init()
        self.display.hw.clear()
        time.sleep(0.2)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.display.image)
        draw.rectangle((10, 10, self.display.width - 10, self.display.height - 10), outline=0, fill=0)
        self.display.ShowImage(self.display.getbuffer(self.display.image))
        time.sleep(1)
        self.display.hw.clear()

        if hasattr(self.display, "_is_mock") and self.display._is_mock():
            logger.info("Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

        self.timer.status_a = ""
        self.timer.status_b = ""
        self.timer.status_c = self.timer.mode

        self.display.draw_layout(self.timer.open_time, self.timer.close_time, self.timer.status_a, self.timer.status_b, self.timer.status_c)
        self.display.ShowImage(self.display.getbuffer(self.display.image))

    def handle_buttons(self):
        # KEY2: Pause/Resume (short press), Reset (long press)
        if self.buttons.is_pressed('KEY2'):
            if not self.key2_was_pressed:
                self.key2_press_time = time.monotonic()
                self.key2_was_pressed = True
        else:
            if self.key2_was_pressed:
                if self.key2_press_time is not None:
                    duration = time.monotonic() - self.key2_press_time
                    if duration >= 2.0:
                        # Long press: reset
                        self.timer.enabled = False
                        self.timer.elapsed = 0
                        self.timer.show_zero = False
                        self.timer.status = "OPEN"
                        logger.info("Timer stopped and reset (long press).")
                    else:
                        # Short press: pause/resume ONLY
                        if not self.timer.enabled:
                            self.timer.enabled = True
                            self.timer.last_update_time = time.monotonic()
                            logging.info("Timer resumed (short press).")
                        else:
                            self.timer.enabled = False
                            logging.info("Timer paused (short press).")
                self.key2_press_time = None
                self.key2_was_pressed = False

        # KEY3: select OPEN timer for editing
        if self.buttons.is_pressed('KEY3'):
            if self.selected_timer != "OPEN":
                self.selected_timer = "OPEN"
                logging.info("Selected OPEN timer for editing.")

        # KEY1: select CLOSE timer for editing
        if self.buttons.is_pressed('KEY1'):
            if self.selected_timer != "CLOSE":
                self.selected_timer = "CLOSE"
                logging.info("Selected CLOSE timer for editing.")

        # KEY2: exit selection mode if in selection
        if self.selected_timer and self.buttons.is_pressed('KEY2'):
            logging.info(f"Exited selection mode for {self.selected_timer}.")
            self.selected_timer = None

        # Joystick up/down: adjust selected timer value
        if self.selected_timer:
            if self.joystick.is_active('up'):
                if self.selected_timer == "OPEN":
                    self.timer.open_time += 1
                    logging.info("Increased OPEN time to %d", self.timer.open_time)
                elif self.selected_timer == "CLOSE":
                    self.timer.close_time += 1
                    logging.info("Increased CLOSE time to %d", self.timer.close_time)
                time.sleep(0.2)  # Debounce

            if self.joystick.is_active('down'):
                if self.selected_timer == "OPEN":
                    self.timer.open_time = max(0, self.timer.open_time - 1)
                    logging.info("Decreased OPEN time to %d", self.timer.open_time)
                elif self.selected_timer == "CLOSE":
                    self.timer.close_time = max(0, self.timer.close_time - 1)
                    logging.info("Decreased CLOSE time to %d", self.timer.close_time)
                time.sleep(0.2)  # Debounce

        if self.joystick.is_active('right'):
            if self.selected_timer == "OPEN":
                self.timer.open_time = max(0, self.timer.open_time - 1)
                logging.info("Decreased OPEN time to %d", self.timer.open_time)
            elif self.selected_timer == "CLOSE":
                self.timer.close_time = max(0, self.timer.close_time - 1)
                logging.info("Decreased CLOSE time to %d", self.timer.close_time)
            elif self.selected_timer is None:
                # Toggle random mode when no timer is selected
                self.timer.toggle_random_mode()
                logging.info("Toggled to %s mode", self.timer.mode)
            time.sleep(0.2)  # Debounce

    def log_timer_state_changes(self):
        # Only log when something actually changes
        if self.timer.enabled != self._last_timer_enabled:
            logger.debug(f"Timer enabled changed: {self._last_timer_enabled} -> {self.timer.enabled}")
            self._last_timer_enabled = self.timer.enabled

        if self.timer.status != self._last_timer_status:
            logger.debug(f"Timer status changed: {self._last_timer_status} -> {self.timer.status}")
            self._last_timer_status = self.timer.status

        if self.timer.mode != self._last_timer_mode:
            logger.debug(f"Timer mode changed: {self._last_timer_mode} -> {self.timer.mode}")
            self._last_timer_mode = self.timer.mode

        if self.timer.elapsed != self._last_timer_elapsed:
            if int(self.timer.elapsed) != int(self._last_timer_elapsed):
                logger.debug(f"Timer elapsed changed: {int(self._last_timer_elapsed)} -> {int(self.timer.elapsed)}")
            self._last_timer_elapsed = self.timer.elapsed

    def run(self):
        try:
            while self.running:
                self.handle_buttons()
                if self.timer.enabled:
                    self.timer.update()
                    # Animate classic spinner for status_a
                    now = time.monotonic()
                    if now - self._last_anim_time > 0.2:
                        self._clock_index = (self._clock_index + 1) % len(self._clock_symbols)
                        self._last_anim_time = now
                    self.timer.status_a = self._clock_symbols[self._clock_index]
                else:
                    self.timer.status_a = ""
                self.display.update_values(self.timer)
                self.display.ShowImage(self.display.getbuffer(self.display.image))
                self.log_timer_state_changes()
                time.sleep(0.1)
        finally:
            self.buttons.cleanup()
            self.joystick.cleanup()
            if hasattr(self.display, "hw") and hasattr(self.display.hw, "RPI"):
                try:
                    self.display.hw.RPI.module_exit()
                    logger.info("GPIO cleanup done.")
                except Exception as e:
                    logger.error("GPIO cleanup failed: %s", e)