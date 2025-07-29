from PIL import Image, ImageDraw, ImageFont
import os
import platform

OPEN_TEXT = "OPEN:"
CLOSE_TEXT = "CLOSE:"

def _get_display_driver():
    driver_type = os.getenv("DISPLAY_DRIVER")
    if driver_type == "mock":
        from features.steps.mocks.mock_sh1106 import SH1106
        return SH1106
    elif driver_type == "real":
        from device.SH1106 import SH1106
        return SH1106
    else:
        if platform.machine().startswith('arm'):
            from device.SH1106 import SH1106
            return SH1106
        else:
            from features.steps.mocks.mock_sh1106 import SH1106
            return SH1106

class Display:
    def __init__(self, hardware=None):
        # If hardware is provided, use it. Otherwise, instantiate selected driver with no args.
        if hardware is None:
            driver = _get_display_driver()
            self.hw = driver()
        else:
            self.hw = hardware
        self.width = self.hw.width
        self.height = self.hw.height
        self.font_main = self._get_font(14)
        self.font_status = self._get_font(10)
        self.image = Image.new('1', (self.hw.width, self.hw.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)

    def getbuffer(self, image):
        return self.hw.getbuffer(image)

    def ShowImage(self, image):
        """Show image and if using mock, save PNG automatically."""
        result = self.hw.ShowImage(image)
        self._save_if_mock()
        return result

    def show(self):
        """Convenience for showing the current image buffer."""
        self.ShowImage(self.getbuffer(self.image))

    def _get_font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def _draw_label_number(self, y, label, number):
        label_x = 5
        number = str(number)
        bbox = self.font_main.getbbox(number)
        num_w = bbox[2] - bbox[0]
        num_x = self.width - num_w - 5
        self.draw.text((label_x, y), label, font=self.font_main, fill=0)
        self.draw.text((num_x, y), number, font=self.font_main, fill=0)

    def draw_layout(self, open_num, close_num, status_a, status_b, status_c):
        # Clear display
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)

        # Status bar at top (height 16px)
        status_h = 16
        self.draw.rectangle((0, 0, self.width - 1, status_h - 1), outline=0, fill=100)

        # Status A (left), Status B (center), Status C (right-aligned)
        self.draw.text((2, 2), str(status_a), font=self.font_status, fill=0)
        status_b_text = str(status_b)
        bbox_b = self.font_status.getbbox(status_b_text)
        status_b_w = bbox_b[2] - bbox_b[0]
        status_b_x = (self.width - status_b_w) // 2
        self.draw.text((status_b_x, 2), status_b_text, font=self.font_status, fill=0)
        status_c_text = str(status_c)
        bbox_c = self.font_status.getbbox(status_c_text)
        status_c_w = bbox_c[2] - bbox_c[0]
        status_c_x = self.width - status_c_w - 2
        self.draw.text((status_c_x, 2), status_c_text, font=self.font_status, fill=0)

        # Main numbers
        self._draw_label_number(28, OPEN_TEXT, open_num)
        self._draw_label_number(48, CLOSE_TEXT, close_num)

    def update_numbers(self, open_num, close_num):
        # Only update the main numbers, keep status bar as is
        self.draw.rectangle((0, 20, self.width, self.height), fill=255)
        self._draw_label_number(28, OPEN_TEXT, open_num)
        self._draw_label_number(48, CLOSE_TEXT, close_num)

    def save(self, path):
        """Save the current PIL image buffer to disk as PNG."""
        self.image.save(path)

    def _is_mock(self):
        # Detect if hardware is mock by module path or by class name
        return "features.steps.mocks" in self.hw.__class__.__module__

    def _save_if_mock(self, path="mock_output.png"):
        if self._is_mock():
            self.image.save(path)

if __name__ == "__main__":
    display = Display()
    display.draw_layout(
        open_num=42,
        close_num=7,
        status_a="A", status_b="B", status_c="C"
    )
    display.show()