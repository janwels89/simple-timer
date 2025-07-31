from behave import given, when, then
from app.input import ButtonInput, _get_gpio_module
from unittest.mock import patch
import time


@given("the timer is disabled")
def step_timer_disabled(context):
    context.timer.enabled = False

@when('the user presses {key}')
@when('the user presses {key} for {seconds:d} seconds')
def step_press_key_for_seconds(context, key, seconds=2):
    GPIO = _get_gpio_module()
    pin = context.buttons._pin_mapping[key]
    with patch("time.sleep", return_value=None):
        # Simulate press
        GPIO._press(pin)
        # Call controller logic to process the press
        context.controller.handle_buttons()

        # Simulate "holding" the button (sleep is mocked, so instant)
        import time
        time.sleep(seconds)

        # Simulate release
        GPIO._release(pin)
        # Call controller logic again to process the release
        context.controller.handle_buttons()

@then("the timer module selected should be OPEN")
def step_check_timer_mode_open(context):
    assert context.timer.status == "OPEN", f"Expected mode 'OPEN', but got '{context.timer.status}'"

@then("the timer module selected should be CLOSE")
def step_check_timer_mode_close(context):
    assert context.timer.status == "CLOSE", f"Expected mode 'CLOSE', but got '{context.timer.status}'"

@then("the timer should be enabled")
def step_timer_should_be_enabled(context):
    assert context.timer.enabled, "Expected timer to be enabled, but it is disabled"

@then('the timer settings are reset')
def then_timer_settings_are_reset(context):
    # Ensure settings are reloaded after reset for assertion
    context.timer.load_settings()
    assert context.timer.open_time == context.timer.DEFAULT_OPEN_TIME, "Open time not reset to default"
    assert context.timer.close_time == context.timer.DEFAULT_CLOSE_TIME, "Close time not reset to default"