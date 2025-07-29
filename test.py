from app.display import Display
from PIL import Image, ImageDraw
import time
import logging

logger = logging.getLogger(__name__)

d = None
try:
    d = Display()
    logger.info("Loaded driver: %s from module: %s", d.hw.__class__, d.hw.__class__.__module__)
    d.hw.Init()
    d.hw.clear()
    time.sleep(0.2)

    image = Image.new('1', (d.width, d.height), "WHITE")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, d.width-10, d.height-10), outline=0, fill=0)
    logger.info("Sending visible pattern to display")
    d.ShowImage(d.getbuffer(image))
    logger.info("Pattern sent")
    time.sleep(2)

finally:
    if d is not None and hasattr(d, "hw") and hasattr(d.hw, "RPI"):
        try:
            d.hw.RPI.module_exit()
            logger.info("GPIO cleanup done.")
        except Exception as e:
            logger.error("GPIO cleanup failed: %s", e)