from behave import given, when, then
from app.timer import TimerController
from app.display import Display

@given('the timer starts with default values')
def step_timer_default(context):
    context.timer = TimerController()
    context.display = Display()

@when('the application runs')
def step_application_runs(context):
    # Simulate drawing the layout on the display with current timer values
    timer = context.timer
    display = context.display
    display.draw_layout(timer.open_time, timer.close_time, "", "", "")
    # Optionally, you might want to "show" the image if your mock/test setup expects it
    display.ShowImage(display.getbuffer(display.image))

@when('the user increments the OPEN timer')
def step_increment_open(context):
    context.timer.status = "OPEN"
    context.timer.increase_time()

@then('the display should show "{expected}" for OPEN')
def step_display_shows_open(context, expected):
    display_value = str(context.display._last_state["open_num"])
    timer_value = str(context.timer.open_time)
    assert display_value == expected, f"Expected OPEN to show {expected}, but display showed {display_value}"
    assert timer_value == expected, f"Expected timer OPEN value to be {expected}, but got {timer_value}"

@then('the display should show "{expected}" for CLOSE')
def step_display_shows_close(context, expected):
    actual = context.timer.close_time
    assert str(actual) == expected, f"Expected CLOSE to show {expected}, but got {actual}"