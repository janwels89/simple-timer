import time
import logging

logger = logging.getLogger(__name__)

LCD_WIDTH   = 128
LCD_HEIGHT  = 64

class SH1106(object):
    """
    Mock version of the SH1106 display class for testing.
    Simulates display buffer and outputs to console instead of hardware.
    """
    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        self.buffer = []  # Stores "drawn" operations as logs
        self.is_cleared = False

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
        # Just return a fake buffer
        return [0x00] * ((self.width//8) * self.height)

    def ShowImage(self, pBuf):
        # Log the image buffer display
        self.buffer.append(f"[MOCK] ShowImage called with buffer size {len(pBuf)}")

    def clear(self):
        # Simulate clearing the display
        self.buffer.append("[MOCK] clear display")
        self.is_cleared = True

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