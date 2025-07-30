from behave import when, then, given
import math

@when('the user moves the joystick right')
def step_move_joystick_right(context):
    timer = context.timer
    if getattr(timer, "mode", "loop") != "random":
        timer.mode = "random"
        if hasattr(timer, "randomize_if_needed"):
            timer.randomize_if_needed()
    else:
        timer.mode = "loop"
        if hasattr(timer, "randomize_if_needed"):
            timer.randomize_if_needed()

@then('the timer mode should be "{expected_mode}"')
def step_timer_mode_should_be(context, expected_mode):
    assert hasattr(context.timer, "mode"), "Timer object has no 'mode' attribute"
    assert context.timer.mode == expected_mode, f"Expected timer mode '{expected_mode}', got '{context.timer.mode}'"

@then('the OPEN time should remain {expected:d} seconds')
def step_open_time_should_remain(context, expected):
    # Check for a base value if present, else fall back to open_time
    open_base = getattr(context.timer, "open_time_base", context.timer.open_time)
    assert math.isclose(open_base, expected, abs_tol=0.1), f"Expected OPEN base time {expected}, got {open_base}"

@then('the CLOSE time should remain {expected:d} seconds')
def step_close_time_should_remain(context, expected):
    close_base = getattr(context.timer, "close_time_base", context.timer.close_time)
    assert math.isclose(close_base, expected, abs_tol=0.1), f"Expected CLOSE base time {expected}, got {close_base}"

@when('the timer starts a new period')
def step_timer_starts_new_period(context):
    # This simulates a period transition; in real use, update() would do this
    # We'll force a transition and re-randomize if needed
    if hasattr(context.timer, "randomize_if_needed"):
        context.timer.randomize_if_needed()
    context.last_period_open = getattr(context.timer, "open_time", None)
    context.last_period_close = getattr(context.timer, "close_time", None)

@then('the displayed period time should be between 0 and its base time')
def step_period_time_between_zero_and_base(context):
    # Check both open and close, one of them should be active
    if context.timer.status == "OPEN":
        period = context.timer.open_time
        base = getattr(context.timer, "open_time_base", period)
    elif context.timer.status == "CLOSE":
        period = context.timer.close_time
        base = getattr(context.timer, "close_time_base", period)
    else:
        assert False, f"Unknown timer status {context.timer.status}"
    assert 0 <= period <= base, f"Period time {period} not between 0 and {base}"

@then('the base OPEN and CLOSE times should not change')
def step_base_open_close_should_not_change(context):
    open_base = getattr(context.timer, "open_time_base", context.timer.open_time)
    close_base = getattr(context.timer, "close_time_base", context.timer.close_time)
    assert math.isclose(open_base, 10, abs_tol=0.1), f"Expected OPEN base time 10, got {open_base}"
    assert math.isclose(close_base, 5, abs_tol=0.1), f"Expected CLOSE base time 5, got {close_base}"


@given('the timer mode is "{mode}"')
def step_timer_mode_is(context, mode):
    context.timer.mode = mode
    # Re-randomize times if needed
    if hasattr(context.timer, "randomize_if_needed"):
        context.timer.randomize_if_needed()

@then('the timer should use the OPEN and CLOSE base times')
def step_timer_uses_base_times(context):
    open_base = getattr(context.timer, "open_time_base", context.timer.open_time)
    close_base = getattr(context.timer, "close_time_base", context.timer.close_time)
    assert math.isclose(context.timer.open_time, open_base, abs_tol=0.1), f"Timer's open_time {context.timer.open_time} != base {open_base}"
    assert math.isclose(context.timer.close_time, close_base, abs_tol=0.1), f"Timer's close_time {context.timer.close_time} != base {close_base}"

@when('a new period starts')
def step_new_period_starts(context):
    # Simulate a period transition (OPEN <-> CLOSE)
    # Save previous period time for later comparison
    if not hasattr(context, "previous_period_time"):
        context.previous_period_time = None
    if context.timer.status == "OPEN":
        context.previous_period_time = context.timer.open_time
        context.timer.status = "CLOSE"
    else:
        context.previous_period_time = context.timer.close_time
        context.timer.status = "OPEN"
    # Re-randomize if in random mode
    if hasattr(context.timer, "randomize_if_needed"):
        context.timer.randomize_if_needed()

@then('the new period time should be different from the previous period and between 0 and its base time')
def step_new_period_time_is_random_and_in_bounds(context):
    # Depending on status, check the appropriate value
    if context.timer.status == "OPEN":
        period = context.timer.open_time
        base = getattr(context.timer, "open_time_base", period)
    else:
        period = context.timer.close_time
        base = getattr(context.timer, "close_time_base", period)
    prev = getattr(context, "previous_period_time", None)
    assert 0 <= period <= base, f"Period time {period} not between 0 and {base}"
    if prev is not None:
        # Allow slight float imprecision to still detect a real change
        assert not math.isclose(period, prev, abs_tol=0.01), f"Period time {period} unexpectedly equal to previous {prev}"

@then('the base times should not change')
def step_base_times_should_not_change(context):
    # These should remain at their original test values (commonly 10 and 5)
    open_base = getattr(context.timer, "open_time_base", context.timer.open_time)
    close_base = getattr(context.timer, "close_time_base", context.timer.close_time)
    # Optionally, use context-stored initial values if tracked, else default to 10/5
    expected_open = getattr(context, "expected_open_time", 10)
    expected_close = getattr(context, "expected_close_time", 5)
    assert math.isclose(open_base, expected_open, abs_tol=0.1), f"Expected OPEN base time {expected_open}, got {open_base}"
    assert math.isclose(close_base, expected_close, abs_tol=0.1), f"Expected CLOSE base time {expected_close}, got {close_base}"

@then('the timer completes a period')
def step_timer_completes_period(context):
    # Simulate the end of the current period
    # Transition as in update logic, including show_zero if used
    if hasattr(context.timer, "show_zero"):
        context.timer.show_zero = True
    # Call update if available to process transition
    if hasattr(context.timer, "update"):
        context.timer.update()

@given('the timer completes a period')
def step_timer_completes_period(context):
    """
    Simulate the timer completing its current period (OPEN or CLOSE).
    This advances the timer to the next period, as if time had elapsed.
    The last period time is stored in context for later checks.
    """
    if context.timer.status == "OPEN":
        context.last_period_time = context.timer.open_time
        context.timer.status = "CLOSE"
    else:
        context.last_period_time = context.timer.close_time
        context.timer.status = "OPEN"
    # Trigger randomization if in random mode
    if hasattr(context.timer, "randomize_if_needed"):
        context.timer.randomize_if_needed()