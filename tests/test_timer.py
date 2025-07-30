from app.timer import TimerController

def test_timercontroller_init_and_update(tmp_path, monkeypatch):
    # Patch settings file location to avoid writing to real file system
    monkeypatch.setattr("app.timer.SETTINGS_FILE", str(tmp_path / "settings.json"))
    t = TimerController()
    orig_open = t.open_time
    orig_close = t.close_time
    t.open_time = 2
    t.close_time = 1
    t.status = "OPEN"
    t.elapsed = 0
    t.show_zero = False
    t.enabled = True
    t.last_update_time -= 2  # Simulate 2 seconds passing
    t.update()
    # After update, should have show_zero True and elapsed advanced
    assert t.show_zero is True or t.elapsed > 0
    # Test saving and loading settings
    t.save_settings()
    t.open_time = 999
    t.close_time = 999
    t.load_settings()
    assert t.open_time == 2
    assert t.close_time == 1

def test_timercontroller_adjust_and_reset(tmp_path, monkeypatch):
    monkeypatch.setattr("app.timer.SETTINGS_FILE", str(tmp_path / "settings.json"))
    t = TimerController()
    t.open_time = 5
    t.close_time = 5
    t.status = "OPEN"
    t.adjust_time(2)
    assert t.open_time == 7
    t.status = "CLOSE"
    t.adjust_time(-3)
    assert t.close_time == 2
    t.reset_settings()
    assert t.open_time == t.DEFAULT_OPEN_TIME
    assert t.close_time == t.DEFAULT_CLOSE_TIME