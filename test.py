import time
from app.input import ButtonInput, JoystickInput
from app.utils import run_with_thinkerer

def test_logic(sh1106):
    from app.display import Display
    from PIL import Image, ImageDraw, ImageFont

    display = Display(hardware=sh1106)
    display.hw.Init()
    display.hw.clear()

    # Use a basic monospaced font (Thinkerer works best with this)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None  # fallback

    boot_msg = "Press buttons"
    print(boot_msg)

    def draw_message(msg):
        img = Image.new('1', (display.width, display.height), 255)  # 255=white background for mode '1'
        draw = ImageDraw.Draw(img)
        # Draw black rectangle as border for visibility
        draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=0, fill=255)
        # Draw text in black (0)
        draw.text((2, display.height // 2 - 8), msg, font=font, fill=0)
        display.ShowImage(display.getbuffer(img))

    draw_message(boot_msg)

    buttons = ButtonInput()
    joystick = JoystickInput()

    def show_message_on_display(message, duration=1.0):
        draw_message(message)
        time.sleep(duration)
        draw_message(boot_msg)

    try:
        last_pressed = set()
        last_dirs = set()
        while True:
            pressed = set(buttons.pressed_buttons())
            new_presses = pressed - last_pressed
            for button in new_presses:
                msg = f"{button} pressed!"
                print(msg)
                show_message_on_display(msg, duration=1.0)
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

if __name__ == "__main__":
    run_with_thinkerer(test_logic, app_name="Test")