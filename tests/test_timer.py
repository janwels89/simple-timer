import os
import pytest
from app.timer import TimerController

@pytest.fixture
def tmp_settings_file(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr("app.timer.SETTINGS_FILE", str(settings_file))
    yield str(settings_file)

def test_timer_init_defaults(tmp_settings_file):
    t = TimerController()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME
    assert t.status == "OPEN"
    assert t.mode == "loop"
    assert t.mode == "loop"
    assert t.enabled is False
    assert t.elapsed == 0
    assert isinstance(t.last_update_time, float)
    assert t.show_zero is False

def test_timer_save_and_load_settings(tmp_settings_file):
    t = TimerController()
    t._open_time_base = 12
    t._close_time_base = 21
    t.save_settings()
    t._open_time_base = 1
    t._close_time_base = 2
    t.load_settings()
    assert t.open_time == 12
    assert t.close_time == 21

def test_timer_load_settings_handles_missing_or_bad_file(tmp_settings_file):
    t = TimerController()
    if os.path.exists(tmp_settings_file):
        os.remove(tmp_settings_file)
    t._open_time_base = 123
    t._close_time_base = 456
    t.load_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME

    # Write bad JSON
    with open(tmp_settings_file, "w") as f:
        f.write("{bad json")
    t._open_time_base = 3
    t._close_time_base = 4
    t.load_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME

def test_timer_reset_settings(tmp_settings_file):
    t = TimerController()
    t._open_time_base = 42
    t._close_time_base = 24
    t.save_settings()
    assert os.path.exists(tmp_settings_file)
    t.reset_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME
    assert os.path.exists(tmp_settings_file)

def test_timer_adjust_time_and_clamp(tmp_settings_file):
    t = TimerController()
    t._open_time_base = 2
    t.status = "OPEN"
    t.adjust_time(-5)
    assert t._open_time_base == 1  # Clamp to 1, not 0
    t.status = "CLOSE"
    t._close_time_base = 2
    t.adjust_time(-5)
    assert t._close_time_base == 1

import time

def test_timer_enable_and_update(tmp_settings_file):
    t = TimerController()
    t.enabled = True
    t.status = "OPEN"
    t.open_time = 1
    t.elapsed = 0
    t.show_zero = False

    # Simulate enough time has passed for the timer to "expire"
    t.last_update_time -= 2  # More than t.open_time

    old_status = t.status

    t.update()
    assert t.show_zero is True
    assert t.status == old_status

    # Simulate more time passing before the second update
    t.last_update_time -= 2  # Add this line!
    t.update()
    assert t.status != old_status
    assert t.show_zero is False

def test_timer_update_when_disabled(tmp_settings_file):
    t = TimerController()
    t.enabled = False
    t.last_update_time -= 10
    t.elapsed = 0
    t.update()
    assert t.elapsed == 0

def test_timer_set_mode(tmp_settings_file):
    t = TimerController()
    t.set_mode("loop")
    assert t.mode == "loop"
    t.set_mode("random")
    assert t.mode == "random"
    with pytest.raises(ValueError):
        t.set_mode("nonexistent")