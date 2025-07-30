import time

def before_scenario(context, scenario):
    # Set up fake monotonic time and patch for all steps in the scenario
    context._original_monotonic = time.monotonic
    context._fake_time = context._original_monotonic()
    def fake_monotonic():
        return context._fake_time
    time.monotonic = fake_monotonic

def after_scenario(context, scenario):
    # Restore the original monotonic after scenario
    if hasattr(context, "_original_monotonic"):
        time.monotonic = context._original_monotonic