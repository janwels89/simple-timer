import time
import sys
import logging
from app.timer import TimerController
from app.display import Display
from app.input import ButtonInput

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

def main(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.debug("main() starting, debug=%s", debug)

    display = None
    buttons = None

    try:
        display = Display()
        display.hw.Init()
        display.hw.clear()
        time.sleep(0.2)

        from PIL import ImageDraw
        draw = ImageDraw.Draw(display.image)
        draw.rectangle((10, 10, display.width - 10, display.height - 10), outline=0, fill=0)
        display.ShowImage(display.getbuffer(display.image))
        time.sleep(1)
        display.hw.clear()
        logger.info("start timer")

        timer = TimerController()
        timer.enabled = False  # Ensure timer does not start automatically

        timer.status_a = ""
        timer.status_b = ""
        timer.status_c = timer.mode

        if hasattr(display, "_is_mock") and display._is_mock():
            logger.info("Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

        display.draw_layout(timer.open_time, timer.close_time, timer.status_a, timer.status_b, timer.status_c)
        display.ShowImage(display.getbuffer(display.image))

        buttons = ButtonInput()

        key2_was_pressed = False

        while True:
            # --- KEY2: Start/Stop timer toggle ---
            if buttons.is_pressed('KEY2'):
                if not key2_was_pressed:
                    if not timer.enabled:
                        timer.enabled = True
                        timer.last_update_time = time.monotonic()  # Reset to prevent jump
                        logger.info("Timer started.")
                    else:
                        timer.enabled = False
                        logger.info("Timer stopped.")
                    key2_was_pressed = True
            else:
                key2_was_pressed = False

            # --- KEY3: select OPEN timer
            if buttons.is_pressed('KEY3'):
                if timer.mode != "OPEN":
                    timer.mode = "OPEN"
                    logger.info("Timer module selected: OPEN")

            # --- KEY1: select CLOSE timer
            if buttons.is_pressed('KEY1'):
                if timer.mode != "CLOSE":
                    timer.mode = "CLOSE"
                    logger.info("Timer module selected: CLOSE")

            # Only update timer if enabled
            if timer.enabled:
                timer.update()

            # Update display
            display.update_numbers(timer)
            display.ShowImage(display.getbuffer(display.image))
            time.sleep(0.1)

    finally:
        if buttons is not None:
            buttons.cleanup()
        if display is not None and hasattr(display, "hw") and hasattr(display.hw, "RPI"):
            try:
                display.hw.RPI.module_exit()
                logger.info("GPIO cleanup done.")
            except Exception as e:
                logger.error("GPIO cleanup failed: %s", e)

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    try:
        main(debug=debug)
    except Exception as e:
        logger.exception("Exception occurred")