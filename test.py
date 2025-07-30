import time
from app.input import ButtonInput, JoystickInput

# Import Display class
try:
    from app.display import Display
    from PIL import ImageDraw, Image
    display = Display()
    display.hw.Init()
    display.hw.clear()
    # Draw rectangle for initial test
    draw = ImageDraw.Draw(display.image)
    draw.rectangle((10, 10, display.width - 10, display.height - 10), outline=0, fill=1)
    display.ShowImage(display.getbuffer(display.image))
    time.sleep(1)

    # Flash the display (fill black then restore)
    flash_img = Image.new('1', (display.width, display.height), 0)
    display.ShowImage(display.getbuffer(flash_img))
    time.sleep(0.2)
    display.ShowImage(display.getbuffer(display.image))
    time.sleep(0.5)

    # Clear display and set blank background
    display.hw.clear()
    display.background = Image.new('1', (display.width, display.height), 1)
    display.ShowImage(display.getbuffer(display.background))
except Exception as e:
    print("Display test skipped or failed:", e)
    display = None

# Input test section
buttons = ButtonInput()
joystick = JoystickInput()

print("Testing buttons (KEY1/2/3) and joystick (up/down/left/right/press). Press Ctrl+C to exit.")

try:
    while True:
        # Buttons
        pressed = buttons.pressed_buttons()
        for button in pressed:
            print(f"{button} pressed!")

        # Joystick
        directions = joystick.active_directions()
        for d in directions:
            print(f"Joystick {d} active!")

        time.sleep(0.1)
finally:
    buttons.cleanup()
    joystick.cleanup()
    if display is not None:
        try:
            display.hw.clear()
        except Exception:
            pass