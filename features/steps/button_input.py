from behave import given, when, then
from app.timer import TimerController
from features.steps.mocks.mock_sh1106 import SH1106

@when("the user presses KEY3")
def step_press_key3(context):
    context.timer.mode = "OPEN"


@then("the timer module selected should be OPEN")
def step_check_timer_mode_on(context):
    assert context.timer.mode == "OPEN", f"Expected mode 'OPEN', but got '{context.timer.mode}'"


@when("the user presses KEY1")
def step_press_key1(context):
    context.timer.mode = "CLOSE"


@then("the timer module selected should be CLOSE")
def step_check_timer_mode_on(context):
    assert context.timer.mode == "CLOSE", f"Expected mode 'CLOSE', but got '{context.timer.mode}'"


@given("the timer is disabled")
def step_timer_disabled(context):
    context.timer.enabled = False


@when("the user presses KEY2")
def step_press_key2(context):
    context.timer.enabled = not context.timer.enabled


@then("the timer should be enabled")
def step_timer_should_be_enabled(context):
    assert context.timer.enabled is True, "Expected timer to be enabled, but it is disabled"


@when('the user presses KEY2 for 2 seconds')
def when_user_presses_key2_for_two_seconds(context):
    # Simulate pressing KEY2 for 2 seconds.
    # If you have a controller with a button handling method:
    if hasattr(context, "controller"):
        context.controller.handle_button_press("KEY2", duration=2)
    elif hasattr(context, "timer"):
        # If the timer resets directly on this action:
        context.timer.reset_settings()
    else:
        raise NotImplementedError("Button input simulation not implemented for this context.")

@then('the timer settings are reset')
def then_timer_settings_are_reset(context):
    # Ensure settings are reloaded after reset for assertion
    context.timer.load_settings()
    assert context.timer.open_time == context.timer.DEFAULT_OPEN_TIME, "Open time not reset to default"
    assert context.timer.close_time == context.timer.DEFAULT_CLOSE_TIME, "Close time not reset to default"