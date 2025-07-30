from behave import given, when, then
from app.timer import TimerController
from app.display import Display
from features.steps.mocks.mock_sh1106 import SH1106
from features.steps.mocks.mock_input import ButtonInput
from PIL import Image, ImageDraw, ImageFont



@given("the device is powered on")
def step_powered_on(context):
    context.timer = TimerController()
    context.display = Display(SH1106())
    context.buttons = ButtonInput()
    context.timer.status = "OPEN"


@given("a timer (OPEN or CLOSE) is selected")
def step_timer_selected(context):
    context.timer.status = "OPEN"


@given("the selected timer is currently set to {value:d} seconds")
def step_set_timer_value(context, value):
    if context.timer.status == "OPEN":
        context.timer.open_time = value
    elif context.timer.status == "CLOSE":
        context.timer.close_time = value
    else:
        raise ValueError("Timer mode must be set to 'OPEN' or 'CLOSE' before setting time.")

@when("the user moves the joystick {direction}")
def step_move_joystick(context, direction):
    if context.timer.status == "OPEN":
        context.previous_timer_value = context.timer.open_time
    elif context.timer.status == "CLOSE":
        context.previous_timer_value = context.timer.close_time
    else:
        raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    if direction == "up":
        context.timer.increase_time()
    elif direction == "down":
        context.timer.decrease_time()
    else:
        raise ValueError(f"Unknown joystick direction: {direction}")

    # Prepare a new image
    WIDTH, HEIGHT = context.display.width, context.display.height
    image = Image.new("1", (WIDTH, HEIGHT), "WHITE")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # Or use truetype

    # Draw text
    draw.text((0, 0), f"OPEN: {context.timer.open_time}s", font=font, fill=0)
    draw.text((0, 10), f"CLOSE: {context.timer.close_time}s", font=font, fill=0)

    # Convert to display buffer and show
    pBuf = context.display.getbuffer(image)
    context.display.ShowImage(pBuf)

@then("the selected timer value should {change} by 1 second")
def step_check_timer_changed(context, change):
    if change == "increase":
        expected = context.previous_timer_value + 1
    elif change == "decrease":
        expected = context.previous_timer_value - 1
    else:
        raise ValueError(f"Unknown change: {change}")

    if context.timer.status == "OPEN":
        actual = context.timer.open_time
    elif context.timer.status == "CLOSE":
        actual = context.timer.close_time
    else:
        raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    assert actual == expected, f"Expected timer value {expected}, but got {actual}"


@then('the display should show the updated timer value')
def step_impl(context):
    # Use the status values from context (they should not be changed here)
    # Only open_num and close_num reflect the timer update
    context.display.update_values(context.timer)

    # Optionally, save the image for inspection
    context.display.save("test_output.png")