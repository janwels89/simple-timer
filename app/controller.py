import time
import logging
from app.timer import TimerController
from app.display import Display
from app.input import ButtonInput

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
        self.running = True
        self.key2_was_pressed = False
        self.key2_press_time = None

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
                        # Long press: stop and reset timer
                        self.timer.enabled = False
                        self.timer.elapsed = 0
                        self.timer.show_zero = False
                        self.timer.status = "OPEN"
                        logger.info("Timer stopped and reset (long press).")
                    else:
                        # Short press: toggle pause/resume
                        if not self.timer.enabled:
                            self.timer.enabled = True
                            self.timer.last_update_time = time.monotonic()
                            logger.info("Timer started/resumed (short press).")
                        else:
                            self.timer.enabled = False
                            logger.info("Timer paused (short press).")
                self.key2_press_time = None
                self.key2_was_pressed = False

        # KEY3: select OPEN timer
        if self.buttons.is_pressed('KEY3'):
            if self.timer.mode != "OPEN":
                self.timer.mode = "OPEN"
                logger.info("Timer module selected: OPEN")

        # KEY1: select CLOSE timer
        if self.buttons.is_pressed('KEY1'):
            if self.timer.mode != "CLOSE":
                self.timer.mode = "CLOSE"
                logger.info("Timer module selected: CLOSE")

        # You can add joystick/button handling for time adjustment here if needed

    def run(self):
        try:
            while self.running:
                self.handle_buttons()
                if self.timer.enabled:
                    self.timer.update()
                self.display.update_numbers(self.timer)
                self.display.ShowImage(self.display.getbuffer(self.display.image))
                time.sleep(0.1)
        finally:
            self.buttons.cleanup()
            if hasattr(self.display, "hw") and hasattr(self.display.hw, "RPI"):
                try:
                    self.display.hw.RPI.module_exit()
                    logger.info("GPIO cleanup done.")
                except Exception as e:
                    logger.error("GPIO cleanup failed: %s", e)