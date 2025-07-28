from behave import given, when, then
from app.timer import TimerController
from app.mock_hardware import WaveI2COLED


@given("the device is powered on")
def step_powered_on(context):
    context.timer = TimerController()
    context.display = WaveI2COLED()
    context.timer.mode = "ON"


@given("a timer (ON or OFF) is selected")
def step_timer_selected(context):
    context.timer.mode = "ON"


@given("the selected timer is currently set to {value:d} seconds")
def step_set_timer_value(context, value):
    if context.timer.mode == "ON":
        context.timer.on_time = value
    elif context.timer.mode == "OFF":
        context.timer.off_time = value
    else:
        raise ValueError("Timer mode must be set to 'ON' or 'OFF' before setting time.")

@when("the user moves the joystick {direction}")
def step_move_joystick(context, direction):
    if context.timer.mode == "ON":
        context.previous_timer_value = context.timer.on_time
    elif context.timer.mode == "OFF":
        context.previous_timer_value = context.timer.off_time
    else:
        raise ValueError("Timer mode must be 'ON' or 'OFF'")

    if direction == "up":
        context.timer.increase_time()
    elif direction == "down":
        context.timer.decrease_time()
    else:
        raise ValueError(f"Unknown joystick direction: {direction}")

    context.display.clear()
    context.display.text(f"ON: {context.timer.on_time}s", 0, 0)
    context.display.text(f"OFF: {context.timer.off_time}s", 0, 10)
    context.display.show()


@then("the selected timer value should {change} by 1 second")
def step_check_timer_changed(context, change):
    if change == "increase":
        expected = context.previous_timer_value + 1
    elif change == "decrease":
        expected = context.previous_timer_value - 1
    else:
        raise ValueError(f"Unknown change: {change}")

    if context.timer.mode == "ON":
        actual = context.timer.on_time
    elif context.timer.mode == "OFF":
        actual = context.timer.off_time
    else:
        raise ValueError("Timer mode must be 'ON' or 'OFF'")

    assert actual == expected, f"Expected timer value {expected}, but got {actual}"


@then("the display should show the updated timer value")
def step_check_display_text(context):
    expected_value = None
    if context.timer.mode == "ON":
        expected_value = context.timer.on_time
    elif context.timer.mode == "OFF":
        expected_value = context.timer.off_time
    else:
        raise ValueError("Timer mode must be 'ON' or 'OFF'")

    displayed_text = context.display.last_text
    assert str(expected_value) in displayed_text, (
        f"Expected display to show timer value {expected_value}, but got '{displayed_text}'"
    )