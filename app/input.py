import RPi.GPIO as GPIO

class ButtonInput:
    """
    Handles KEY1, KEY2, KEY3 for Waveshare 1.3inch OLED HAT.
    Call is_pressed('KEY1'), is_pressed('KEY2'), is_pressed('KEY3').
    """
    # Internal mapping for Waveshare 1.3inch OLED HAT
    _pin_mapping = {
        "KEY1": 22,
        "KEY2": 23,
        "KEY3": 24,
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self._pin_mapping.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self, key_name):
        pin = self._pin_mapping.get(key_name)
        if pin is None:
            raise ValueError(f"Unknown button: {key_name}")
        return GPIO.input(pin) == GPIO.LOW

    def pressed_buttons(self):
        return [name for name, pin in self._pin_mapping.items() if GPIO.input(pin) == GPIO.LOW]

    def cleanup(self):
        GPIO.cleanup()


class JoystickInput:
    """
    Handles 5-way joystick for Waveshare 1.3inch OLED HAT.
    Directions: 'up', 'down', 'left', 'right', 'press'
    """
    _pin_mapping = {
        "up": 6,
        "down": 19,
        "left": 5,
        "right": 26,
        "press": 13,
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self._pin_mapping.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_active(self, direction):
        pin = self._pin_mapping.get(direction)
        if pin is None:
            raise ValueError(f"Unknown joystick direction: {direction}")
        return GPIO.input(pin) == GPIO.LOW

    def active_directions(self):
        return [name for name, pin in self._pin_mapping.items() if GPIO.input(pin) == GPIO.LOW]

    def cleanup(self):
        GPIO.cleanup()