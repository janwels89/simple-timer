from app.display import Display
from PIL import Image, ImageDraw

import time

d = None
try:
    d = Display()
    print("Loaded driver:", d.hw.__class__, "from module:", d.hw.__class__.__module__)
    d.hw.Init()
    d.hw.clear()
    time.sleep(0.2)  # Brief pause to ensure display is ready

    # Create an image with a visible pattern (black rectangle inside white background)
    image = Image.new('1', (d.width, d.height), "WHITE")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, d.width-10, d.height-10), outline=0, fill=0)  # Draw a filled black rectangle

    print("Sending visible pattern to display")
    d.ShowImage(d.getbuffer(image))
    print("Pattern sent")

    # Optional: Keep the pattern visible for a while
    time.sleep(2)

finally:
    # Clean up GPIOs
    if d is not None and hasattr(d, "hw") and hasattr(d.hw, "RPI"):
        try:
            d.hw.RPI.module_exit()
            print("GPIO cleanup done.")
        except Exception as e:
            print("GPIO cleanup failed:", e)
