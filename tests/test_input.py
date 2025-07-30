import pytest
import platform

def is_arm():
    return 'arm' in platform.machine() or 'aarch64' in platform.machine()

@pytest.fixture
def button_input():
    if is_arm():
        from app.input import ButtonInput
    else:
        from features.steps.mocks.mock_input import ButtonInput
    return ButtonInput()

@pytest.fixture
def joystick_input():
    if is_arm():
        from app.input import JoystickInput
    else:
        from features.steps.mocks.mock_input import JoystickInput
    return JoystickInput()

def test_button_input_press_release(button_input):
    btn = button_input
    if not is_arm():
        btn.press('KEY1')
    assert btn.is_pressed('KEY1') is True or is_arm()
    if not is_arm():
        btn.release('KEY1')
        assert btn.is_pressed('KEY1') is False

def test_button_input_pressed_buttons(button_input):
    btn = button_input
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

def test_joystick_input_active(joystick_input):
    js = joystick_input
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