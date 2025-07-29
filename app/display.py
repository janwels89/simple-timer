from PIL import Image, ImageDraw, ImageFont

OPEN_TEXT = "OPEN:"
CLOSE_TEXT = "CLOSE:"

class Display:
    def __init__(self, hardware):
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
        return self.hw.ShowImage(image)

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

        # Main field area (below status bar)
        gap = 2
        main1_y = status_h + gap
        main2_y = main1_y + 20 + gap  # ~20px for main text 1

        # Draw rectangle around main field area
        main_field_top = status_h
        main_field_bottom = self.height - 1
        self.draw.rectangle(
            (0, main_field_top, self.width - 1, main_field_bottom),
            outline=0, fill=None
        )

        # Draw OPEN and CLOSE lines inside main field
        self._draw_label_number(main1_y, OPEN_TEXT, open_num)
        self._draw_label_number(main2_y, CLOSE_TEXT, close_num)

    def update_numbers(self, open_num, close_num):
        """
        Update only the OPEN and CLOSE numbers in the main area, preserving the rest of the display.
        """
        # Status bar at top (height 16px)
        status_h = 16
        gap = 2
        main1_y = status_h + gap
        main2_y = main1_y + 20 + gap  # ~20px for main text 1

        # Clear previous numbers by overdrawing with white rectangles
        # Compute vertical space for each number line
        number_height = 18  # estimated height for font size 14

        # Clear OPEN number line
        self.draw.rectangle(
            (0, main1_y, self.width, main1_y + number_height),
            fill=255
        )
        # Redraw OPEN label and number
        self._draw_label_number(main1_y, OPEN_TEXT, open_num)

        # Clear CLOSE number line
        self.draw.rectangle(
            (0, main2_y, self.width, main2_y + number_height),
            fill=255
        )
        # Redraw CLOSE label and number
        self._draw_label_number(main2_y, CLOSE_TEXT, close_num)

        # Update the display
        self.ShowImage(self.getbuffer(self.image))


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