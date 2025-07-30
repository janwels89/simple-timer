import time
from app.input import ButtonInput
from app.display import Display
from PIL import Image, ImageDraw

def initial_display_test(display):
    """Show initial test pattern or message on display."""
    display.hw.Init()
    display.hw.clear()
    time.sleep(0.2)
    draw = ImageDraw.Draw(display.image)
    draw.rectangle((10, 10, display.width - 10, display.height - 10), outline=0, fill=0)
    display.ShowImage(display.getbuffer(display.image))
    time.sleep(1)
    display.hw.clear()

def flash_display(display, duration=0.2):
    """Flash the display by filling it black briefly."""
    flash_img = Image.new('1', (display.width, display.height), 0)
    display.ShowImage(display.getbuffer(flash_img))
    time.sleep(duration)
    display.ShowImage(display.getbuffer(display.background))  # restore

def main():
    buttons = ButtonInput()
    display = Display()
    initial_display_test(display)  # Call initial display test first

    print("Press any button (KEY1, KEY2, KEY3) to flash display. Ctrl+C to exit.")
    try:
        while True:
            pressed = buttons.pressed_buttons()
            if pressed:
                print(f"Button(s) pressed: {pressed} -> Flashing display!")
                flash_display(display)
                # Debounce: wait for release
                while buttons.pressed_buttons():
                    time.sleep(0.01)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        buttons.cleanup()
        if hasattr(display, "hw") and hasattr(display.hw, "RPI"):
            display.hw.RPI.module_exit()

if __name__ == "__main__":
    main()