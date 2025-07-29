import os
import platform
from PIL import Image, ImageDraw, ImageFont

def _get_display_driver(debug=False):
    driver_type = os.getenv("DISPLAY_DRIVER")
    if driver_type == "mock":
        from features.steps.mocks.mock_sh1106 import SH1106
        if debug:
            print("[DEBUG] Using MOCK display driver (forced by DISPLAY_DRIVER=mock)")
        return SH1106
    elif driver_type == "real":
        from device.SH1106 import SH1106
        if debug:
            print("[DEBUG] Using REAL display driver (forced by DISPLAY_DRIVER=real)")
        return SH1106
    else:
        arch = platform.machine().lower()
        if any(arm in arch for arm in ("arm", "aarch64")):
            from device.SH1106 import SH1106
            if debug:
                print("[DEBUG] Using REAL display driver (platform is ARM)")
            return SH1106
        else:
            from features.steps.mocks.mock_sh1106 import SH1106
            if debug:
                print("[DEBUG] Using MOCK display driver (platform is NOT ARM)")
            return SH1106

class Display:
    def __init__(self, hardware=None, debug=False):
        self._debug = debug
        if self._debug:
            print("[DEBUG] Display.__init__ starting")
        # If hardware is provided, use it. Otherwise, instantiate selected driver with no args.
        if hardware is None:
            driver = _get_display_driver(debug=self._debug)
            self.hw = driver()
            if self._debug:
                print(f"[DEBUG] Loaded display driver: {self.hw.__class__.__module__}.{self.hw.__class__.__name__}")
        else:
            self.hw = hardware
            if self._debug:
                print(f"[DEBUG] Using provided hardware: {self.hw.__class__.__module__}.{self.hw.__class__.__name__}")
        self.width = self.hw.width
        self.height = self.hw.height
        self.font_main = self._get_font(14)
        self.font_status = self._get_font(10)
        self.image = Image.new('1', (self.hw.width, self.hw.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)
        if self._debug:
            print("[DEBUG] Display.__init__ complete")

    def _is_mock(self):
        # Detect if hardware is mock by module path
        return "features.steps.mocks" in self.hw.__class__.__module__

    def getbuffer(self, image):
        if self._debug:
            print("[DEBUG] Display.getbuffer called")
        return self.hw.getbuffer(image)

    def ShowImage(self, image):
        if self._debug:
            print("[DEBUG] Display.ShowImage called")
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

    def draw_layout(self, open_num, close_num, status_a, status_b, status_c):
        if self._debug:
            print(f"[DEBUG] Display.draw_layout called: open={open_num}, close={close_num}, a={status_a}, b={status_b}, c={status_c}")
        # ... (rest of your drawing code, unchanged)

    def update_numbers(self, open_num, close_num):
        if self._debug:
            print(f"[DEBUG] Display.update_numbers called: open={open_num}, close={close_num}")
        # ... (rest of your update code, unchanged)