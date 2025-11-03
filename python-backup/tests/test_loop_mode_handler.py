import pytest
from app.timer import TimerController, LoopModeHandler

@pytest.fixture
def timer():
    t = TimerController()
    t.set_mode("loop")
    return t

@pytest.fixture
def handler(timer):
    return LoopModeHandler(timer)

def test_initialize_sets_times(timer, handler):
    timer._open_time_base = 8
    timer._close_time_base = 6
    timer.status = "OPEN"
    handler.initialize()
    assert timer.open_time == 8
    assert timer.close_time == 6

def test_transition_open_to_close(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 5
    timer._close_time_base = 3
    handler.initialize()
    handler.transition()
    assert timer.status == "CLOSE"
    assert timer.close_time == 3
    assert timer.next_time == 5

def test_transition_close_to_open(timer, handler):
    timer.status = "CLOSE"
    timer._open_time_base = 4
    timer._close_time_base = 7
    handler.initialize()
    handler.transition()
    assert timer.status == "OPEN"
    assert timer.open_time == 4
    assert timer.next_time == 7

def test_adjust_time_open(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 5
    handler.adjust_time(2)
    assert timer._open_time_base == 7
    handler.adjust_time(-10)
    assert timer._open_time_base == 1

def test_adjust_time_close(timer, handler):
    timer.status = "CLOSE"
    timer._close_time_base = 5
    handler.adjust_time(2)
    assert timer._close_time_base == 7
    handler.adjust_time(-10)
    assert timer._close_time_base == 1

def test_current_remaining_time(timer, handler):
    timer.status = "OPEN"
    timer.open_time = 10
    timer.elapsed = 3
    assert handler.current_remaining_time() == 7
    timer.status = "CLOSE"
    timer.close_time = 5
    timer.elapsed = 2
    assert handler.current_remaining_time() == 3