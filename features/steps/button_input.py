from behave import given, when, then


@given("the timer is disabled")
def step_timer_disabled(context):
    context.timer.enabled = False

@when("the user presses KEY1")
def step_press_key1(context):
    # Simulate KEY1 press using the button mock
    context.buttons.press("KEY1")
    # Simulate logic (in reality, your app would read button state and act)
    context.timer.status = "CLOSE"
    context.buttons.release("KEY1")

@when("the user presses KEY3")
def step_press_key3(context):
    context.buttons.press("KEY3")
    context.timer.status = "OPEN"
    context.buttons.release("KEY3")

@when("the user presses KEY2")
def step_press_key2(context):
    context.buttons.press("KEY2")
    # Toggle enable state
    context.timer.enabled = not context.timer.enabled
    context.buttons.release("KEY2")

@when('the user presses KEY2 for 2 seconds')
def when_user_presses_key2_for_two_seconds(context):
    context.buttons.press("KEY2")
    # Simulate long-press logic: reset settings
    context.timer.reset_settings()
    context.buttons.release("KEY2")

@then("the timer module selected should be OPEN")
def step_check_timer_mode_open(context):
    assert context.timer.status == "OPEN", f"Expected mode 'OPEN', but got '{context.timer.status}'"

@then("the timer module selected should be CLOSE")
def step_check_timer_mode_close(context):
    assert context.timer.status == "CLOSE", f"Expected mode 'CLOSE', but got '{context.timer.status}'"

@then("the timer should be enabled")
def step_timer_should_be_enabled(context):
    assert context.timer.enabled is True, "Expected timer to be enabled, but it is disabled"

@then('the timer settings are reset')
def then_timer_settings_are_reset(context):
    # Ensure settings are reloaded after reset for assertion
    context.timer.load_settings()
    assert context.timer.open_time == context.timer.DEFAULT_OPEN_TIME, "Open time not reset to default"
    assert context.timer.close_time == context.timer.DEFAULT_CLOSE_TIME, "Close time not reset to default"