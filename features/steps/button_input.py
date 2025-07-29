from behave import given, when, then
from app.timer import TimerController
from app.mock_hardware import WaveI2COLED


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



@then("the timer should be disabled")
def step_timer_should_be_disabled(context):
    assert context.timer.enabled is False, "Expected timer to be disabled, but it is enabled"