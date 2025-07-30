import sys
import os
import pytest

# Add the repo root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.timer import TimerController

@pytest.fixture
def tmp_settings_file(tmp_path, monkeypatch):
    # Patch the settings file location to avoid writing to the real file system
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("app.timer.SETTINGS_FILE", str(settings_file))
    yield str(settings_file)

def test_init_defaults(tmp_settings_file):
    t = TimerController()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME
    assert t.status == "OPEN"
    assert t.mode == "loop"
    assert t.enabled is False
    assert t.elapsed == 0
    assert isinstance(t.last_update_time, float)
    assert t.show_zero is False

def test_save_and_load_settings(tmp_settings_file):
    t = TimerController()
    t.open_time = 12
    t.close_time = 21
    t.save_settings()
    t.open_time = 1
    t.close_time = 2
    t.load_settings()
    assert t.open_time == 12
    assert t.close_time == 21

def test_load_settings_handles_missing_or_bad_file(tmp_settings_file):
    t = TimerController()
    # Remove settings file if present
    if os.path.exists(tmp_settings_file):
        os.remove(tmp_settings_file)
    t.open_time = 123
    t.close_time = 456
    t.load_settings()
    # Should reset to defaults if file missing
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME

    # Write bad JSON
    with open(tmp_settings_file, "w") as f:
        f.write("{bad json")
    t.open_time = 3
    t.close_time = 4
    t.load_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME

def test_reset_settings(tmp_settings_file):
    t = TimerController()
    t.open_time = 42
    t.close_time = 24
    t.save_settings()
    assert os.path.exists(tmp_settings_file)
    t.reset_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME
    assert os.path.exists(tmp_settings_file)

def test_adjust_time_and_no_negatives(tmp_settings_file):
    t = TimerController()
    t.open_time = 2
    t.status = "OPEN"
    t.adjust_time(-5)
    assert t.open_time == 0  # Should not be negative
    t.status = "CLOSE"
    t.close_time = 2
    t.adjust_time(-5)
    assert t.close_time == 0  # Should not be negative

def test_increase_and_decrease_time(tmp_settings_file):
    t = TimerController()
    t.open_time = 2
    t.status = "OPEN"
    t.increase_time()
    assert t.open_time == 3
    t.decrease_time()
    t.decrease_time()
    t.decrease_time()
    assert t.open_time == 0  # Never goes below zero

def test_update_transitions(tmp_settings_file):
    t = TimerController()
    t.open_time = 2
    t.close_time = 3
    t.status = "OPEN"
    t.elapsed = 0
    t.show_zero = False
    t.enabled = True

    # Fast-forward time: simulate 2 seconds passed
    t.last_update_time -= 2
    t.update()
    # After open period, should show zero
    assert t.show_zero is True
    assert t.status == "OPEN"

    # Call update again, should switch to CLOSE and reset elapsed
    t.update()
    assert t.status == "CLOSE"
    assert t.elapsed == 0
    assert not t.show_zero

    # Simulate close period
    t.last_update_time -= 3
    t.update()
    assert t.show_zero is True
    assert t.status == "CLOSE"

    # Call update again, should switch to OPEN and reset elapsed
    t.update()
    assert t.status == "OPEN"
    assert t.elapsed == 0

def test_update_when_disabled(tmp_settings_file):
    t = TimerController()
    t.enabled = False
    t.last_update_time -= 10
    t.elapsed = 0
    t.update()
    # Should not change anything
    assert t.elapsed == 0