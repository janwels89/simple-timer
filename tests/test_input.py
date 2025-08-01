import pytest

@pytest.fixture
def button_input():
    from app.input import ButtonInput
    return ButtonInput()

@pytest.fixture
def joystick_input():
    from app.input import JoystickInput
    return JoystickInput()

def test_button_input_press_release(button_input):
    # Use the pin mapping from the class
    key1_pin = button_input._pin_mapping['KEY1']
    # Use the GPIO module imported in app.input
    from app.input import GPIO
    GPIO._press(key1_pin)
    assert button_input.is_pressed('KEY1')
    GPIO._release(key1_pin)
    assert not button_input.is_pressed('KEY1')

def test_button_input_pressed_buttons(button_input):
    key1_pin = button_input._pin_mapping['KEY1']
    key2_pin = button_input._pin_mapping['KEY2']
    from app.input import GPIO
    GPIO._press(key1_pin)
    GPIO._press(key2_pin)
    pressed = button_input.pressed_buttons()
    assert 'KEY1' in pressed
    assert 'KEY2' in pressed
    GPIO._release(key1_pin)
    pressed = button_input.pressed_buttons()
    assert 'KEY1' not in pressed
    assert 'KEY2' in pressed

def test_joystick_input_active(joystick_input):
    up_pin = joystick_input._pin_mapping['up']
    right_pin = joystick_input._pin_mapping['right']
    press_pin = joystick_input._pin_mapping['press']
    from app.input import GPIO
    GPIO._press(up_pin)
    assert joystick_input.is_active('up')
    GPIO._press(right_pin)
    actives = joystick_input.active_directions()
    assert 'up' in actives and 'right' in actives
    GPIO._release(up_pin)
    assert not joystick_input.is_active('up')
    GPIO._press(press_pin)
    assert joystick_input.is_active('press')
    GPIO._release(press_pin)
    assert not joystick_input.is_active('press')