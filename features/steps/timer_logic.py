from behave import given, when, then
from app.timer import TimerController

@given("the OPEN time is set to {seconds:d} seconds")
def step_set_open_time(context, seconds):
    context.timer.open_time = seconds
    context.timer._open_time_base = seconds
    context.timer.save_settings()

@given("the CLOSE time is set to {seconds:d} seconds")
def step_set_close_time(context, seconds):
    context.timer.close_time = seconds
    context.timer._close_time_base = seconds
    context.timer.save_settings()

@given("the timer is running")
def step_timer_running(context):
    context.timer.enabled = True
    context.timer.status = "OPEN"
    context.timer.elapsed = 0

@when('{seconds:d} seconds have passed')
def step_advance_time(context, seconds):
    # You may need to advance your timer's time source here if using a fake clock
    if hasattr(context, "_fake_time"):
        context._fake_time += seconds
    context.timer.update()

@then('the output should be OPEN for {seconds:d} seconds')
def step_check_output_open_duration(context, seconds):
    assert context.timer.status == "OPEN", f"Expected mode OPEN, but got {context.timer.status}"
    assert context.timer.open_time == seconds, f"Expected OPEN time {seconds}, but got {context.timer.open_time}"

@then('CLOSE for {seconds:d} seconds')
def step_check_close_time(context, seconds):
    assert context.timer.close_time == seconds, f"Expected CLOSE time {seconds}, but got {context.timer.close_time}"

@when("the device is rebooted")
def step_reboot_device(context):
    context.timer = TimerController()

@then("the OPEN time should be {seconds:d} seconds")
def step_check_open_time(context, seconds):
    assert context.timer.open_time == seconds, (
        f"Expected OPEN time {seconds}, but got {context.timer.open_time}"
    )

@then("the CLOSE time should be {seconds:d} seconds")
def step_check_close_time(context, seconds):
    assert context.timer.close_time == seconds, (
        f"Expected CLOSE time {seconds}, but got {context.timer.close_time}"
    )

@when("the timer settings are reset")
@given("the timer settings are reset")
def step_reset_timer_settings(context):
    context.timer.reset_settings()