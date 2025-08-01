from behave import given, when, then
from app.timer import TimerController
from app.display import Display

@given('the timer starts with default values')
def step_timer_default(context):
    context.timer = TimerController()
    context.display = Display()
    # Draw initial layout
    context.display.draw_layout(context.timer.open_time, context.timer.close_time, "", "", "")
    context.display.ShowImage(context.display.getbuffer(context.display.image))

@when('the application runs')
def step_application_runs(context):
    # Redraw the layout on the display with current timer values
    context.display.draw_layout(context.timer.open_time, context.timer.close_time, "", "", "")
    context.display.ShowImage(context.display.getbuffer(context.display.image))

@when('the user increments the OPEN timer')
def step_increment_open(context):
    context.timer.status = "OPEN"
    context.timer.adjust_time(1)
    # Update display after increment
    context.display.draw_layout(context.timer.open_time, context.timer.close_time, "", "", "")
    context.display.ShowImage(context.display.getbuffer(context.display.image))

@then('the display should show "{expected}" for OPEN')
def step_display_shows_open(context, expected):
    # If display has an update_values method, call it
    if hasattr(context.display, "update_values"):
        context.display.update_values(context.timer)
    display_value = str(getattr(context.display, "_last_state", {}).get("open_num", context.timer.open_time))
    timer_value = str(context.timer.open_time)
    assert display_value == expected, f"Expected OPEN to show {expected}, but display showed {display_value}"
    assert timer_value == expected, f"Expected timer OPEN value to be {expected}, but got {timer_value}"

@then('the display should show "{expected}" for CLOSE')
def step_display_shows_close(context, expected):
    # If display has an update_values method, call it
    if hasattr(context.display, "update_values"):
        context.display.update_values(context.timer)
    display_value = str(getattr(context.display, "_last_state", {}).get("close_num", context.timer.close_time))
    timer_value = str(context.timer.close_time)
    assert display_value == expected, f"Expected CLOSE to show {expected}, but display showed {display_value}"
    assert timer_value == expected, f"Expected timer CLOSE value to be {expected}, but got {timer_value}"