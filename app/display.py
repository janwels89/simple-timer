#Display Control

from PIL import Image, ImageDraw, ImageFont

class Display:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.font = ImageFont.load_default()
        self.image = Image.new('1', (self.width, self.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)

    def draw_layout(self, timer_value):
        # Clear image
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)
        # Draw static parts
        self.draw.rectangle((0, 0, self.width - 1, 10), outline=0, fill=255)
        self.draw.text((2, 2), "MY TIMER", font=self.font, fill=0)
        # Draw dynamic part
        self.draw.text((10, 30), f"Timer: {timer_value}", font=self.font, fill=0)

    def show(self):
        self.image.show()

    def save(self, filename):
        self.image.save(filename)

if __name__ == "__main__":
    display = Display()
    display.draw_layout(42)  # Example timer value
    display.show()