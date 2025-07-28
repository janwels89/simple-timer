from behave import given, when, then


@given("the device is powered on")
def step_powered_on(context):
    pass  # Placeholder


@given("a timer (ON or OFF) is selected")
def step_timer_selected(context):
    pass


@given("the selected timer is currently set to 5 seconds")
def step_timer_is_5(context):
    pass


@when("the user moves the joystick up")
def step_joystick_up(context):
    pass


@then("the selected timer value should increase by 1 second")
def step_timer_increased(context):
    pass


@then("the display should show the updated timer value")
def step_display_shows_new(context):
    pass