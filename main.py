import time
import sys
import logging
from app.timer import TimerController
from app.display import Display

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
        timer.status_a = ""
        timer.status_b = ""
        timer.status_c = timer.mode

        if hasattr(display, "_is_mock") and display._is_mock():
            logger.info("Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

        display.draw_layout(timer.open_time, timer.close_time, timer.status_a, timer.status_b, timer.status_c)
        display.ShowImage(display.getbuffer(display.image))

        while True:
            timer.update()
            logger.debug("Timer status=%s elapsed=%s open=%s close=%s", timer.status, timer.elapsed,
                         timer.open_time, timer.close_time)

            display.update_numbers(timer)
            display.ShowImage(display.getbuffer(display.image))
            logger.debug("Status: %s, Elapsed: %.2fs, Open: %s, Close: %s", timer.status, timer.elapsed,
                        timer.open_time, timer.close_time)

    finally:
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