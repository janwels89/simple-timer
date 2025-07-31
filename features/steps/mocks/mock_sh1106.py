import time
import logging
import platform

try:
    import tkinter as tk
    from PIL import Image, ImageTk  # Pillow must be installed
except ImportError:
    tk = None  # If Tkinter is not available, fallback to console-only
    Image = None
    ImageTk = None

logger = logging.getLogger(__name__)

LCD_WIDTH   = 128
LCD_HEIGHT  = 64

def is_x64():
    arch = platform.machine().lower()
    return 'x86_64' in arch or 'amd64' in arch

class SH1106(object):
    """
    Mock version of the SH1106 display class for testing.
    Simulates display buffer and outputs to console and (optionally) a Tkinter window.
    """
    _thinkerer = None  # Singleton for the display GUI

    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        self.buffer = []  # Stores "drawn" operations as logs
        self.is_cleared = False
        self.last_image = None  # For display in Tkinter

        # Only show the GUI if on x64 and Tkinter is available and not already started
        if is_x64() and tk and SH1106._thinkerer is None:
            SH1106._thinkerer = Thinkerer(self.width, self.height)
        self.thinkerer = SH1106._thinkerer

    def command(self, cmd):
        # Log the command instead of sending to hardware
        self.buffer.append(f"[MOCK] command: {hex(cmd)}")

    def Init(self):
        # Simulate initialization sequence
        self.buffer.append("[MOCK] Init called")
        self.reset()
        for cmd in [
            0xAE, 0x02, 0x10, 0x40, 0x81, 0xA0, 0xC0, 0xA6, 0xA8, 0x3F, 0xD3, 0x00,
            0xd5, 0x80, 0xD9, 0xF1, 0xDA, 0x12, 0xDB, 0x40, 0x20, 0x02, 0xA4, 0xA6
        ]:
            self.command(cmd)
        time.sleep(0.1)
        self.command(0xAF)
        self.buffer.append("[MOCK] Display initialized")

    def reset(self):
        # Simulate a hardware reset
        self.buffer.append("[MOCK] reset called")
        time.sleep(0.1)

    def getbuffer(self, image):
        # Simulate getting a buffer from an image
        self.buffer.append("[MOCK] getbuffer called")
        # Save the latest image for GUI display
        self.last_image = image
        return [0x00] * ((self.width//8) * self.height)

    def ShowImage(self, pBuf):
        # Log the image buffer display
        self.buffer.append(f"[MOCK] ShowImage called with buffer size {len(pBuf)}")
        # If there's a GUI, display the last image
        if self.thinkerer and self.last_image:
            self.thinkerer.update_image(self.last_image)

    def clear(self):
        # Simulate clearing the display
        self.buffer.append("[MOCK] clear display")
        self.is_cleared = True
        if self.thinkerer:
            self.thinkerer.clear()

    # Utility for tests: print buffer actions
    def show_log(self):
        logger.info("SH1106 Display Log:")
        for entry in self.buffer:
            logger.info(entry)
        if self.is_cleared:
            logger.info("Display is currently cleared.")

    # Utility for tests: get the last buffer operation
    @property
    def last_operation(self):
        return self.buffer[-1] if self.buffer else None

class Thinkerer:
    """
    Simple Tkinter-based window to display the latest SH1106 image.
    Must be started in the main thread!
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.root = tk.Tk()
        self.root.title("SH1106 Mock Display (Thinkerer)")
        self.root.resizable(False, False)
        self.label = tk.Label(self.root)
        self.label.pack()
        # Do NOT start mainloop here! Must be started in the main thread by your launcher.

    def update_image(self, pil_image):
        if not pil_image or not ImageTk:
            return
        img = pil_image.rotate(180)  # Rotates the image display 180 degrees
        img = img.resize((self.width*3, self.height*3))  # Scale up for visibility
        self.tk_img = ImageTk.PhotoImage(img)
        self.label.configure(image=self.tk_img)
        self.label.image = self.tk_img  # Keep reference

    def clear(self):
        self.label.configure(image=None)
        self.label.image = None