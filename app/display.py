from PIL import Image, ImageDraw, ImageFont

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

    def draw_layout(self, main_text_1, main_num_1, main_text_2, main_num_2, status_a, status_b, status_c):
        # Clear display
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)

        # Status bar at top (height 16px)
        status_h = 16
        bar_splits = [25, 25, 16]
        status_x = [0, bar_splits[0], bar_splits[0] + bar_splits[1]]

        # Draw status bar rectangles (optional for visual split)
        self.draw.rectangle((0, 0, self.width - 1, status_h - 1), outline=0, fill=100)
        #self.draw.rectangle((status_x[0], 0, status_x[0] + bar_splits[0] - 1, status_h - 1), outline=0)
        #self.draw.rectangle((status_x[1], 0, status_x[1] + bar_splits[1] - 1, status_h - 1), outline=0)
        #self.draw.rectangle((status_x[2], 0, status_x[2] + bar_splits[2] - 1, status_h - 1), outline=0)

        # Status texts
        self.draw.text((2, 2), str(status_a), font=self.font_status, fill=0)
        self.draw.text((status_x[1] + 2, 2), str(status_b), font=self.font_status, fill=0)
        self.draw.text((status_x[2] + 2, 2), str(status_c), font=self.font_status, fill=0)

        # Main texts + numbers
        gap = 2
        main1_y = status_h + gap
        main2_y = main1_y + 20 + gap  # ~20px for main text 1

        # --- Main 1: Left-aligned text, right-aligned number ---
        text1 = str(main_text_1)
        num1 = str(main_num_1)
        # Text left
        text1_x = 5
        # Number right
        bbox_num1 = self.font_main.getbbox(num1)
        num1_w = bbox_num1[2] - bbox_num1[0]
        num1_x = self.width - num1_w - 5

        self.draw.text((text1_x, main1_y), text1, font=self.font_main, fill=0)
        self.draw.text((num1_x, main1_y), num1, font=self.font_main, fill=0)

        # --- Main 2: Left-aligned text, right-aligned number ---
        text2 = str(main_text_2)
        num2 = str(main_num_2)
        text2_x = 5
        bbox_num2 = self.font_main.getbbox(num2)
        num2_w = bbox_num2[2] - bbox_num2[0]
        num2_x = self.width - num2_w - 5

        self.draw.text((text2_x, main2_y), text2, font=self.font_main, fill=0)
        self.draw.text((num2_x, main2_y), num2, font=self.font_main, fill=0)

    def show(self):
        self.image.show()

    def save(self, filename):
        self.image.save(filename)

if __name__ == "__main__":
    display = Display()
    display.draw_layout(
        main_text_1="Left Txt 1", main_num_1=42,
        main_text_2="Left Txt 2", main_num_2=7,
        status_a="A", status_b="B", status_c="C"
    )
    display.show()