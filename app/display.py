from PIL import Image, ImageDraw, ImageFont

OPEN_TEXT = "OPEN:"
CLOSE_TEXT = "CLOSE:"

class Display:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.font_main = self._get_font(14)
        self.font_status = self._get_font(10)
        self.image = Image.new('1', (self.width, self.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)

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
        bar_splits = [25, 25, 16]
        status_x = [0, bar_splits[0], bar_splits[0] + bar_splits[1]]

        # Draw status bar rectangle
        self.draw.rectangle((0, 0, self.width - 1, status_h - 1), outline=0, fill=100)

        # Status A (left), Status B (center), Status C (right-aligned)
        self.draw.text((2, 2), str(status_a), font=self.font_status, fill=0)
        # Centered status_b
        status_b_text = str(status_b)
        bbox_b = self.font_status.getbbox(status_b_text)
        status_b_w = bbox_b[2] - bbox_b[0]
        status_b_x = (self.width - status_b_w) // 2
        self.draw.text((status_b_x, 2), status_b_text, font=self.font_status, fill=0)
        # Right-aligned status_c
        status_c_text = str(status_c)
        bbox_c = self.font_status.getbbox(status_c_text)
        status_c_w = bbox_c[2] - bbox_c[0]
        status_c_x = self.width - status_c_w - 2
        self.draw.text((status_c_x, 2), status_c_text, font=self.font_status, fill=0)

        # Main texts + numbers
        gap = 2
        main1_y = status_h + gap
        main2_y = main1_y + 20 + gap  # ~20px for main text 1

        # Draw OPEN and CLOSE lines
        self._draw_label_number(main1_y, OPEN_TEXT, open_num)
        self._draw_label_number(main2_y, CLOSE_TEXT, close_num)

    def show(self):
        self.image.show()

    def save(self, filename):
        self.image.save(filename)

if __name__ == "__main__":
    display = Display()
    display.draw_layout(
        open_num=42,
        close_num=7,
        status_a="A", status_b="B", status_c="C"
    )
    display.show()