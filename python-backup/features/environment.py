import time
import os
from unittest.mock import patch


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

def after_feature(context, feature):
    # Clean up settings.json after each feature to prevent test pollution
    if os.path.exists("settings.json"):
        try:
            os.remove("settings.json")
        except:
            pass


def before_all(context):
    # Patch time.sleep to instantly return, for all steps
    context._sleep_patcher = patch("time.sleep", return_value=None)
    context._sleep_patcher.start()

def after_all(context):
    # Stop the patch after all tests are done
    context._sleep_patcher.stop()