import pytest
from app.timer import TimerController, RandomModeHandler

@pytest.fixture
def timer():
    t = TimerController()
    t.set_mode("random")
    return t

@pytest.fixture
def handler(timer):
    return RandomModeHandler(timer)

def test_initialize_open(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 10
    timer._close_time_base = 20
    handler.initialize()
    assert 1 <= timer.open_time <= 10
    assert 1 <= timer.next_time <= 20

def test_initialize_close(timer, handler):
    timer.status = "CLOSE"
    timer._open_time_base = 10
    timer._close_time_base = 20
    handler.initialize()
    assert 1 <= timer.close_time <= 20
    assert 1 <= timer.next_time <= 10

def test_transition_open_to_close(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 5
    timer._close_time_base = 7
    handler.initialize()
    old_next = timer.next_time
    handler.transition()
    assert timer.status == "CLOSE"
    assert timer.close_time == old_next
    assert 1 <= timer.next_time <= 5

def test_transition_close_to_open(timer, handler):
    timer.status = "CLOSE"
    timer._open_time_base = 5
    timer._close_time_base = 7
    handler.initialize()
    old_next = timer.next_time
    handler.transition()
    assert timer.status == "OPEN"
    assert timer.open_time == old_next
    assert 1 <= timer.next_time <= 7

def test_adjust_time_open(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 4
    handler.adjust_time(3)
    assert timer._open_time_base == 7
    handler.adjust_time(-10)
    assert timer._open_time_base == 1

def test_adjust_time_close(timer, handler):
    timer.status = "CLOSE"
    timer._close_time_base = 4
    handler.adjust_time(3)
    assert timer._close_time_base == 7
    handler.adjust_time(-10)
    assert timer._close_time_base == 1

def test_current_remaining_time(timer, handler):
    timer.status = "OPEN"
    timer.open_time = 10
    timer.elapsed = 3
    assert handler.current_remaining_time() == 7
    timer.status = "CLOSE"
    timer.close_time = 8
    timer.elapsed = 2
    assert handler.current_remaining_time() == 6

def test_randomize_if_needed_reinitializes(timer, handler):
    timer.status = "OPEN"
    timer._open_time_base = 10
    timer._close_time_base = 10
    handler.initialize()
    timer.open_time = 1
    timer.next_time = 1
    handler.randomize_if_needed()
    # Values should be re-randomized
    assert 1 <= timer.open_time <= 10
    assert 1 <= timer.next_time <= 10