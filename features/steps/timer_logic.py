from behave import given, when, then
from time import sleep
from app.timer import TimerController
from app.mock_hardware import WaveI2COLED


@given("the OPEN time is set to {seconds:d} seconds")
def step_set_open_time(context, seconds):
    context.timer.open_time = seconds

@given("the CLOSE time is set to {seconds:d} seconds")
def step_set_close_time(context, seconds):
    context.timer.close_time = seconds

@given("the timer is running")
def step_timer_running(context):
    context.timer.enabled = True
    context.timer.mode = "OPEN"
    context.timer.elapsed = 0

@when('{seconds:d} seconds have passed')
def step_advance_time(context, seconds):
    context.timer.advance_time(seconds)

@then('the output should be OPEN for {seconds:d} seconds')
def step_check_output_open_duration(context, seconds):
    # Check the timer mode is OPEN
    assert context.timer.mode == "OPEN", f"Expected mode OPEN, but got {context.timer.mode}"

    # Check the OPEN time is as expected
    assert context.timer.open_time == seconds, f"Expected OPEN time {seconds}, but got {context.timer.open_time}"


@then('CLOSE for {seconds:d} seconds')
def step_check_close_time(context, seconds):
    assert context.timer.close_time == seconds, f"Expected CLOSE time {seconds}, but got {context.timer.close_time}"


@then('OPEN again after {seconds:d} seconds')
def step_check_open_again_after(context, seconds):
    # Simulate time passing
    context.timer.advance_time(seconds)

    # Check the mode is OPEN
    assert context.timer.mode == "OPEN", f"Expected mode OPEN after {seconds} seconds, but got {context.timer.mode}"