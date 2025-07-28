from behave import given, when, then
from time import sleep
from app.timer import TimerController
from app.mock_hardware import WaveI2COLED


@given("the ON time is set to {seconds:d} seconds")
def step_set_on_time(context, seconds):
    context.timer.on_time = seconds

@given("the OFF time is set to {seconds:d} seconds")
def step_set_off_time(context, seconds):
    context.timer.off_time = seconds

@given("the timer is running")
def step_timer_running(context):
    context.timer.enabled = True
    context.timer.mode = "ON"
    context.timer.elapsed = 0

@when('{seconds:d} seconds have passed')
def step_advance_time(context, seconds):
    context.timer.advance_time(seconds)

@then('the output should be ON for {seconds:d} seconds')
def step_check_output_on_duration(context, seconds):
    # Check the timer mode is ON
    assert context.timer.mode == "ON", f"Expected mode ON, but got {context.timer.mode}"

    # Check the ON time is as expected
    assert context.timer.on_time == seconds, f"Expected ON time {seconds}, but got {context.timer.on_time}"


@then('OFF for {seconds:d} seconds')
def step_check_off_time(context, seconds):
    assert context.timer.off_time == seconds, f"Expected OFF time {seconds}, but got {context.timer.off_time}"


@then('ON again after {seconds:d} seconds')
def step_check_on_again_after(context, seconds):
    # Simulate time passing
    context.timer.advance_time(seconds)

    # Check the mode is ON
    assert context.timer.mode == "ON", f"Expected mode ON after {seconds} seconds, but got {context.timer.mode}"