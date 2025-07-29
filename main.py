import time
import sys
import logging
from app.timer import TimerController
from app.display import Display

# Set up logging
logger = logging.getLogger(__name__)

def main(debug=False):
    logger.debug(f"main() starting, debug={debug}")
    display = None
    try:
        display = Display(debug=debug)
        display.hw.Init()
        display.hw.clear()
        time.sleep(0.2)

        from PIL import ImageDraw
        draw = ImageDraw.Draw(display.image)
        draw.rectangle((10, 10, display.width - 10, display.height - 10), outline=0, fill=0)
        display.ShowImage(display.getbuffer(display.image))
        time.sleep(2)
        display.hw.clear()
        logger.info("Timer starting")

        timer = TimerController()
        timer.status_a = ""
        timer.status_b = ""
        timer.status_c = timer.mode

        if not debug and hasattr(display, "_is_mock") and display._is_mock():
            print("[INFO] Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

        display.draw_layout(timer.open_time, timer.close_time, timer.status_a, timer.status_b, timer.status_c)
        display.ShowImage(display.getbuffer(display.image))  # <-- FIXED

        while True:
            timer.update()
            logger.debug(f"Timer status={timer.status} elapsed={timer.elapsed} open={timer.open_time} close={timer.close_time}")

            display.update_numbers(timer)

            display.ShowImage(display.getbuffer(display.image))  # <-- FIXED
            if debug:
                logger.debug(f"Timer Status: {timer.status}, Elapsed: {timer.elapsed:.2f}s, Open: {timer.open_time}, Close: {timer.close_time}")
            time.sleep(0.9)
    finally:
        # Always clean up GPIOs if present
        if display is not None and hasattr(display, "hw") and hasattr(display.hw, "RPI"):
            try:
                display.hw.RPI.module_exit()
                logger.info("GPIO cleanup done.")
            except Exception as e:
                logger.error(f"GPIO cleanup failed: {e}")

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    try:
        main(debug=debug)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()
