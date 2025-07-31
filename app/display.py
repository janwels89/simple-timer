import os
import platform
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, "fonts", "Font.ttf")


def _get_display_driver():
    driver_type = os.getenv("DISPLAY_DRIVER")
    if driver_type == "mock":
        from features.steps.mocks.mock_sh1106 import SH1106
        logger.debug("Using MOCK display driver (forced by DISPLAY_DRIVER=mock)")
        return SH1106
    elif driver_type == "real":
        from device.SH1106 import SH1106
        logger.debug("Using REAL display driver (forced by DISPLAY_DRIVER=real)")
        return SH1106
    else:
        arch = platform.machine().lower()
        if any(arm in arch for arm in ("arm", "aarch64")):
            from device.SH1106 import SH1106
            logger.debug("Using REAL display driver (platform is ARM)")
            return SH1106
        else:
            from features.steps.mocks.mock_sh1106 import SH1106
            logger.debug("Using MOCK display driver (platform is NOT ARM)")
            return SH1106


class Display:
    def __init__(self, hardware=None):
        logger.debug("Display.__init__ starting")
        if hardware is None:
            driver = _get_display_driver()
            self.hw = driver()
            logger.debug("Loaded display driver: %s.%s", self.hw.__class__.__module__, self.hw.__class__.__name__)
        else:
            self.hw = hardware
            logger.debug("Using provided hardware: %s.%s", self.hw.__class__.__module__, self.hw.__class__.__name__)

        self.status_a = ""
        self.status_b = ""
        self.status_c = ""
        self.width = self.hw.width
        self.height = self.hw.height

        self.font_number = self._get_font(FONT_PATH, 18)
        self.font_label = self._get_font(FONT_PATH, 18)
        self.font_status = self._get_font(FONT_PATH, 10)
        self.font_small = self._get_font(FONT_PATH, 11)
        self._create_background()
        self.image = Image.new('1', (self.hw.width, self.hw.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)
        logger.debug("Display.__init__ complete")

        # Track last state for state-change-only logging
        self._last_state = {}

    def _create_background(self):
        self.background = Image.new('1', (self.width, self.height), "WHITE")
        bg_draw = ImageDraw.Draw(self.background)
        status_h = 16
        bg_draw.rectangle((0, 0, self.width - 1, status_h - 1), outline=0, fill=100)
        section_w = self.width // 3
        bg_draw.text((2, 2), self.status_a, font=self.font_status, fill=0)
        status_b_text = self.status_b
        bbox_b = self.font_status.getbbox(status_b_text)
        status_b_w = bbox_b[2] - bbox_b[0]
        status_b_x = section_w + (section_w - status_b_w) // 2
        bg_draw.text((status_b_x, 2), status_b_text, font=self.font_status, fill=0)
        status_c_text = self.status_c
        section_c_x = 2 * section_w + 2
        bg_draw.text((section_c_x, 2), status_c_text, font=self.font_status, fill=0)

    def _is_mock(self):
        return "features.steps.mocks" in self.hw.__class__.__module__

    def getbuffer(self, image):
        rotated = image.transpose(Image.ROTATE_180)
        return self.hw.getbuffer(rotated)

    def ShowImage(self, image):
        result = self.hw.ShowImage(image)
        if self._is_mock():
            self.image.save("mock_output.png")
        return result

    def save(self, path):
        self.image.save(path)

    def _get_font(self, font_path, size):
        try:
            font = ImageFont.truetype(font_path, size)
            logger.info(f"Loaded {font_path} at size {size}")
            return font
        except Exception as e:
            logger.warning(f"Falling back to default font: {e}")
            return ImageFont.load_default()

    def _draw_label_number(self, y, label, number, base=None, fill=0, next_val=None):
        label_font = self.font_label
        number_font = self.font_number
        small_font = self.font_small

        label_x = 5
        label_y = y
        number_str = str(number)
        label_bbox = label_font.getbbox(label)
        label_h = label_bbox[3] - label_bbox[1]
        number_bbox = number_font.getbbox(number_str)
        number_w = number_bbox[2] - number_bbox[0]
        number_h = number_bbox[3] - number_bbox[1]
        num_x = self.width - number_w - 30
        num_y = y + max(0, (label_h - number_h) // 2) + 2

        self.draw.text((label_x, label_y), label, font=label_font, fill=fill)
        self.draw.text((num_x, num_y), number_str, font=number_font, fill=fill)

        # Draw base value in small font after main value, if provided
        next_x = num_x + number_w + 6
        if base is not None:
            base_str = f"({base})"
            base_bbox = small_font.getbbox(base_str)
            base_w = base_bbox[2] - base_bbox[0]
            base_x = next_x
            base_y = num_y + (number_h - base_bbox[3] + base_bbox[1]) // 2
            self.draw.text((base_x, base_y), base_str, font=small_font, fill=128)
            next_x = base_x + base_w + 8  # space after base value

        # Optionally display next_time for debug/demo
        if next_val is not None:
            next_str = f"→{next_val}"
            next_bbox = small_font.getbbox(next_str)
            next_y = num_y + (number_h - next_bbox[3] + next_bbox[1]) // 2
            self.draw.text((next_x, next_y), next_str, font=small_font, fill=64)

    def _draw_statuses(self):
        font = self.font_status
        # status_a: left bottom
        if getattr(self, "status_a", ""):
            self.draw.text((2, self.height - 12), str(self.status_a), font=font, fill=0)
        # status_b: center bottom
        if getattr(self, "status_b", ""):
            w, _ = self.draw.textsize(str(self.status_b), font=font)
            self.draw.text((self.width // 2 - w // 2, self.height - 12), str(self.status_b), font=font, fill=0)
        # status_c: right bottom
        if getattr(self, "status_c", ""):
            w, _ = self.draw.textsize(str(self.status_c), font=font)
            self.draw.text((self.width - w - 2, self.height - 12), str(self.status_c), font=font, fill=0)

    def _render_status_and_numbers(self, open_num, close_num, status_a, status_b, status_c,
                                  open_base=None, close_base=None, open_next=None, close_next=None):
        self.status_a = status_a
        self.status_b = status_b
        self.status_c = status_c
        self._create_background()
        self.image = self.background.copy()
        self.draw = ImageDraw.Draw(self.image)
        # Pass open_next and close_next to their respective rows
        self._draw_label_number(18, "OPEN", open_num, open_base, next_val=open_next)
        self._draw_label_number(42, "CLOSE", close_num, close_base, next_val=close_next)

    def draw_layout(self, open_num, close_num, status_a, status_b, status_c, open_base=None, close_base=None):
        current_state = {
            'open_num': open_num,
            'close_num': close_num,
            'status_a': status_a,
            'status_b': status_b,
            'status_c': status_c,
            'open_base': open_base,
            'close_base': close_base
        }
        if current_state != self._last_state:
            logger.debug("Display.draw_layout called: open=%s, close=%s, a=%s, b=%s, c=%s, open_base=%s, close_base=%s",
                         open_num, close_num, status_a, status_b, status_c, open_base, close_base)
            self._last_state = current_state.copy()
        self._render_status_and_numbers(open_num, close_num, status_a, status_b, status_c, open_base, close_base)

    def update_values(self, timer, status_a=None, status_b=None, status_c=None):
        is_random = getattr(timer, "mode", "") == "random"
        if timer.status == "OPEN":
            open_remaining = 0 if getattr(timer, "show_zero", False) else max(0, int(round(
                timer.open_time - timer.elapsed)))
            if is_random:
                close_remaining = getattr(timer, "next_time", timer.close_time)  # next CLOSE period
            else:
                close_remaining = timer.close_time  # fixed CLOSE
        else:
            if is_random:
                open_remaining = getattr(timer, "next_time", timer.open_time)  # next OPEN period
            else:
                open_remaining = timer.open_time  # fixed OPEN
            close_remaining = 0 if getattr(timer, "show_zero", False) else max(0, int(round(
                timer.close_time - timer.elapsed)))

        curr_a = status_a if status_a is not None else getattr(timer, "status_a", "")
        curr_b = status_b if status_b is not None else getattr(timer, "status_b", "")
        curr_c = status_c if status_c is not None else getattr(timer, "status_c", "")

        open_base = timer._open_time_base if is_random else None
        close_base = timer._close_time_base if is_random else None

        current_state = {
            'open_remaining': open_remaining,
            'close_remaining': close_remaining,
            'status_a': curr_a,
            'status_b': curr_b,
            'status_c': curr_c,
            'open_base': open_base,
            'close_base': close_base,
        }
        if current_state != self._last_state:
            logger.debug(
                "Display.update_values called: open_remaining=%s, close_remaining=%s, a=%s, b=%s, c=%s, open_base=%s, close_base=%s",
                open_remaining, close_remaining, curr_a, curr_b, curr_c, open_base, close_base
            )
            self._last_state = current_state.copy()
        self._render_status_and_numbers(
            open_remaining, close_remaining, curr_a, curr_b, curr_c, open_base, close_base
        )


if __name__ == "__main__":
    display = Display()
    display.draw_layout(
        open_num=42,
        close_num=7,
        status_a="A", status_b="B", status_c="C",
        open_base=50, close_base=10
    )
    display.ShowImage(display.getbuffer(display.image))