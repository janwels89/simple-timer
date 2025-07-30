import time
from app.input import ButtonInput, JoystickInput

# Import and initialize Display
try:
    from app.display import Display
    from PIL import Image, ImageDraw
    display = Display()
    display.hw.Init()
    display.hw.clear()
    # Boot message on display and console
    boot_msg = "Press buttons (KEY1/2/3/...) or joystick (up/down/left/right/press). Ctrl+C to exit."
    print(boot_msg)
    # Draw the message on display, centered
    img = Image.new('1', (display.width, display.height), 1)
    draw = ImageDraw.Draw(img)
    draw.text((2, display.height // 2 - 8), boot_msg, fill=0)
    display.ShowImage(display.getbuffer(img))
except Exception as e:
    print("Display test skipped or failed:", e)
    display = None

# Initialize inputs
buttons = ButtonInput()
joystick = JoystickInput()

def show_message_on_display(message, duration=1.0):
    """Show a message on the display for a short time, then restore boot prompt."""
    if display:
        try:
            # Show the message
            img = Image.new('1', (display.width, display.height), 1)
            draw = ImageDraw.Draw(img)
            draw.text((2, display.height // 2 - 8), message, fill=0)
            display.ShowImage(display.getbuffer(img))
            time.sleep(duration)
            # Restore boot message
            boot_msg = "Press buttons (KEY1/2/3/...) or joystick (up/down/left/right/press)"
            img2 = Image.new('1', (display.width, display.height), 1)
            draw2 = ImageDraw.Draw(img2)
            draw2.text((2, display.height // 2 - 8), boot_msg, fill=0)
            display.ShowImage(display.getbuffer(img2))
        except Exception as e:
            print("Display show error:", e)

print("Press buttons (KEY1/2/3/...) or joystick (up/down/left/right/press). Ctrl+C to exit.")

try:
    last_pressed = set()
    last_dirs = set()
    while True:
        # BUTTONS
        pressed = set(buttons.pressed_buttons())
        new_presses = pressed - last_pressed
        for button in new_presses:
            msg = f"{button} pressed!"
            print(msg)
            show_message_on_display(msg, duration=1.0)

        # JOYSTICK
        directions = set(joystick.active_directions())
        new_dirs = directions - last_dirs
        for d in new_dirs:
            msg = f"Joystick {d}!"
            print(msg)
            show_message_on_display(msg, duration=1.0)

        last_pressed = pressed
        last_dirs = directions
        time.sleep(0.1)
finally:
    buttons.cleanup()
    joystick.cleanup()
    if display is not None:
        try:
            display.hw.clear()
        except Exception:
            pass
    print("Cleaned up.")