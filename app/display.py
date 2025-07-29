import os
import platform
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def _get_display_driver(debug=False):
    driver_type = os.getenv("DISPLAY_DRIVER")
    if driver_type == "mock":
        from features.steps.mocks.mock_sh1106 import SH1106
        if debug:
            logger.debug("Using MOCK display driver (forced by DISPLAY_DRIVER=mock)")
        return SH1106
    elif driver_type == "real":
        from device.SH1106 import SH1106
        if debug:
            logger.debug("Using REAL display driver (forced by DISPLAY_DRIVER=real)")
        return SH1106
    else:
        arch = platform.machine().lower()
        if any(arm in arch for arm in ("arm", "aarch64")):
            from device.SH1106 import SH1106
            if debug:
                logger.debug("Using REAL display driver (platform is ARM)")
            return SH1106
        else:
            from features.steps.mocks.mock_sh1106 import SH1106
            if debug:
                logger.debug("Using MOCK display driver (platform is NOT ARM)")
            return SH1106


class Display:
    def __init__(self, hardware=None, debug=False):
        self._debug = debug

        if self._debug:
            logger.debug("Display.__init__ starting")
        # If hardware is provided, use it. Otherwise, instantiate selected driver with no args.
        if hardware is None:
            driver = _get_display_driver(debug=self._debug)
            self.hw = driver()
            if self._debug:
                logger.debug(f"Loaded display driver: {self.hw.__class__.__module__}.{self.hw.__class__.__name__}")
        else:
            self.hw = hardware
            if self._debug:
                logger.debug(f"Using provided hardware: {self.hw.__class__.__module__}.{self.hw.__class__.__name__}")

        self.status_a = None
        self.status_b = None
        self.status_c = None
        self.width = self.hw.width
        self.height = self.hw.height
        self.font_main = self._get_font(14)
        self.font_status = self._get_font(10)
        self._create_background()
        self.image = Image.new('1', (self.hw.width, self.hw.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)
        if self._debug:
            logger.debug("Display.__init__ complete")

    def _create_background(self):
        """Draw static layout and store as background image."""
        self.background = Image.new('1', (self.width, self.height), "WHITE")
        bg_draw = ImageDraw.Draw(self.background)

        # --- Static layout drawing from draw_layout ---
        # Status bar at top (height 16px)
        status_h = 16
        bg_draw.rectangle((0, 0, self.width - 1, status_h - 1), outline=0, fill=100)

        # Divide status bar into three equal sections for A, B, C
        section_w = self.width // 3

        # Status A (left)
        bg_draw.text((2, 2), "", font=self.font_status, fill=0)  # Placeholder

        # Status B (center)
        status_b_text = ""
        bbox_b = self.font_status.getbbox(status_b_text)
        status_b_w = bbox_b[2] - bbox_b[0]
        status_b_x = section_w + (section_w - status_b_w) // 2
        bg_draw.text((status_b_x, 2), status_b_text, font=self.font_status, fill=0)

        # Status C (right)
        status_c_text = ""
        section_c_x = 2 * section_w + 2
        bg_draw.text((section_c_x, 2), status_c_text, font=self.font_status, fill=0)
        # Any other static graphics can go here!

    def _is_mock(self):
        # Detect if hardware is mock by module path
        return "features.steps.mocks" in self.hw.__class__.__module__

    def getbuffer(self, image):
        if self._debug:
            logger.debug("Display.getbuffer called")
        return self.hw.getbuffer(image)

    def ShowImage(self, image):
        if self._debug:
            logger.debug("Display.ShowImage called")
        result = self.hw.ShowImage(image)
        if self._is_mock():
            # Save the PIL image (not the buffer) for inspection
            self.image.save("mock_output.png")
        return result

    def save(self, path):
        self.image.save(path)

    def _get_font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


    def _draw_label_number(self, y, label, number, fill=0):
        label_x = 5
        number = str(number)
        bbox = self.font_main.getbbox(number)
        num_w = bbox[2] - bbox[0]
        num_x = self.width - num_w - 5
        self.draw.text((label_x, y), label, font=self.font_main, fill=fill)
        self.draw.text((num_x, y), number, font=self.font_main, fill=fill)


    def draw_layout(self, open_num, close_num, status_a, status_b, status_c):
        if self._debug:
            logger.debug(f"Display.draw_layout called: open={open_num}, close={close_num}, a={status_a}, b={status_b}, c={status_c}")

        # Update status labels for background
        self.status_a = status_a
        self.status_b = status_b
        self.status_c = status_c
        self._create_background()  # Redraw background with new labels

        # Start from background image
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

        # Draw dynamic numbers
        self._draw_label_number(20, "OPEN", open_num)
        self._draw_label_number(40, "CLOSE", close_num)


    def update_numbers(self, timer):
        if self._debug:
            logger.debug(f"Display.update_numbers called: {timer}")

        if timer.status == "OPEN":
            open_remaining = max(0, int(round(timer.open_time - timer.elapsed)))
            close_remaining = timer.close_time
        else:
            open_remaining = timer.open_time
            close_remaining = max(0, int(round(timer.close_time - timer.elapsed)))

        # Start from the background each time
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)

        # Draw only the changing numbers (adjust y positions as needed)
        self._draw_label_number(20, "OPEN", open_remaining)
        self._draw_label_number(40, "CLOSE", close_remaining)

if __name__ == "__main__":
     display = Display()
     display.draw_layout(
        open_num=42,
        close_num=7,
        status_a="A", status_b="B", status_c="C"
     )
     display.ShowImage(display.getbuffer(display.image))
