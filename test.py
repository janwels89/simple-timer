import logging
from app.display import Display
from PIL import Image, ImageDraw
import time

logger = logging.getLogger(__name__)

# Configure logging for test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

d = None
try:
    d = Display()
    logger.info(f"Loaded driver: {d.hw.__class__} from module: {d.hw.__class__.__module__}")
    d.hw.Init()
    d.hw.clear()
    time.sleep(0.2)  # Brief pause to ensure display is ready

    # Create an image with a visible pattern (black rectangle inside white background)
    image = Image.new('1', (d.width, d.height), "WHITE")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, d.width-10, d.height-10), outline=0, fill=0)  # Draw a filled black rectangle

    logger.info("Sending visible pattern to display")
    d.ShowImage(d.getbuffer(image))
    logger.info("Pattern sent")

    # Optional: Keep the pattern visible for a while
    time.sleep(2)

finally:
    # Clean up GPIOs
    if d is not None and hasattr(d, "hw") and hasattr(d.hw, "RPI"):
        try:
            d.hw.RPI.module_exit()
            logger.info("GPIO cleanup done.")
        except Exception as e:
            logger.error(f"GPIO cleanup failed: {e}")
