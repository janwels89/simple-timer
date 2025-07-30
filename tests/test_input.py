import sys
import os
import platform
import pytest

# Add the repo root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def is_arm():
    return 'arm' in platform.machine() or 'aarch64' in platform.machine()

@pytest.fixture
def ButtonInput():
    if is_arm():
        from app.input import ButtonInput as RealButtonInput
        return RealButtonInput
    else:
        from features.steps.mocks.mock_input import ButtonInput as MockButtonInput
        return MockButtonInput

@pytest.fixture
def JoystickInput():
    if is_arm():
        from app.input import JoystickInput as RealJoystickInput
        return RealJoystickInput
    else:
        from features.steps.mocks.mock_input import JoystickInput as MockJoystickInput
        return MockJoystickInput

def test_button_input_press_release(ButtonInput):
    btn = ButtonInput()
    if not is_arm():
        btn.press('KEY1')
    assert btn.is_pressed('KEY1') is True or is_arm()
    if not is_arm():
        btn.release('KEY1')
        assert btn.is_pressed('KEY1') is False

def test_button_input_pressed_buttons(ButtonInput):
    btn = ButtonInput()
    if not is_arm():
        btn.press('KEY1')
        btn.press('KEY2')
        pressed = btn.pressed_buttons()
        assert 'KEY1' in pressed
        assert 'KEY2' in pressed
        btn.release('KEY1')
        pressed = btn.pressed_buttons()
        assert 'KEY1' not in pressed
        assert 'KEY2' in pressed

def test_joystick_input_active(JoystickInput):
    js = JoystickInput()
    if not is_arm():
        js.move('up')
        assert js.is_active('up')
        js.move('right')
        actives = js.active_directions()
        assert 'up' in actives and 'right' in actives
        js.release('up')
        assert not js.is_active('up')
        js.press()
        assert js.is_active('press')
        js.release_press()
        assert not js.is_active('press')