from behave import given, when, then
from app.timer import TimerController
from app.mock_hardware import WaveI2COLED


@given("the device is powered on")
def step_powered_on(context):
    context.timer = TimerController()
    context.display = WaveI2COLED()
    context.timer.mode = "OPEN"


@given("a timer (OPEN or CLOSE) is selected")
def step_timer_selected(context):
    context.timer.mode = "OPEN"


@given("the selected timer is currently set to {value:d} seconds")
def step_set_timer_value(context, value):
    if context.timer.mode == "OPEN":
        context.timer.open_time = value
    elif context.timer.mode == "CLOSE":
        context.timer.close_time = value
    else:
        raise ValueError("Timer mode must be set to 'OPEN' or 'CLOSE' before setting time.")

@when("the user moves the joystick {direction}")
def step_move_joystick(context, direction):
    if context.timer.mode == "OPEN":
        context.previous_timer_value = context.timer.open_time
    elif context.timer.mode == "CLOSE":
        context.previous_timer_value = context.timer.close_time
    else:
        raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    if direction == "up":
        context.timer.increase_time()
    elif direction == "down":
        context.timer.decrease_time()
    else:
        raise ValueError(f"Unknown joystick direction: {direction}")

    context.display.clear()
    context.display.text(f"OPEN: {context.timer.open_time}s", 0, 0)
    context.display.text(f"CLOSE: {context.timer.close_time}s", 0, 10)
    context.display.show()


@then("the selected timer value should {change} by 1 second")
def step_check_timer_changed(context, change):
    if change == "increase":
        expected = context.previous_timer_value + 1
    elif change == "decrease":
        expected = context.previous_timer_value - 1
    else:
        raise ValueError(f"Unknown change: {change}")

    if context.timer.mode == "OPEN":
        actual = context.timer.open_time
    elif context.timer.mode == "CLOSE":
        actual = context.timer.close_time
    else:
        raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    assert actual == expected, f"Expected timer value {expected}, but got {actual}"


@then("the display should show the updated timer value")
def step_check_display_text(context):
    expected_value = None
    if context.timer.mode == "OPEN":
        expected_value = context.timer.open_time
    elif context.timer.mode == "CLOSE":
        expected_value = context.timer.close_time
    else:
        raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    displayed_text = context.display.last_text
    assert str(expected_value) in displayed_text, (
        f"Expected display to show timer value {expected_value}, but got '{displayed_text}'"
    )