import time

def before_scenario(context, scenario):
    # Only patch if not already patched
    if not hasattr(context, "_real_monotonic"):
        context._real_monotonic = time.monotonic
    context._fake_time = 0
    time.monotonic = lambda: context._fake_time

def after_scenario(context, scenario):
    # Only restore if it has been patched
    if hasattr(context, "_real_monotonic"):
        time.monotonic = context._real_monotonic
        del context._real_monotonic