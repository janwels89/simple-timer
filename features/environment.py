import time

def before_scenario(context, scenario):
    # Save the real time.monotonic to restore later
    if not hasattr(context, "_real_monotonic"):
        context._real_monotonic = time.monotonic
    # Start fake time at zero
    context._fake_time = 0
    # Patch time.monotonic to return the test's fake time
    time.monotonic = lambda: context._fake_time

def after_scenario(context, scenario):
    # Restore the real time.monotonic
    if hasattr(context, "_real_monotonic"):
        time.monotonic = context._real_monotonic