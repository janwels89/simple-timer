import RPi.GPIO as GPIO

class ButtonInput:
    """
    Real implementation for multiple button inputs (e.g., up, down, left, right, select).
    """
    def __init__(self, pin_mapping):
        """
        pin_mapping: dict of button_name -> GPIO pin, e.g.
          {'up': 5, 'down': 6, 'left': 13, 'right': 19, 'select': 26}
        """
        self.pin_mapping = pin_mapping
        GPIO.setmode(GPIO.BCM)
        for pin in pin_mapping.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self, button_name):
        pin = self.pin_mapping[button_name]
        # Button pressed == LOW (False)
        return not GPIO.input(pin)

    def pressed_buttons(self):
        return [name for name, pin in self.pin_mapping.items() if not GPIO.input(pin)]

    def cleanup(self):
        GPIO.cleanup()


class JoystickInput:
    """
    Real implementation for a 4-way joystick with center press.
    Directions: up, down, left, right, press
    """
    def __init__(self, pin_mapping):
        """
        pin_mapping: dict of direction -> GPIO pin, e.g.
          {'up': 17, 'down': 27, 'left': 22, 'right': 23, 'press': 24}
        """
        self.pin_mapping = pin_mapping
        GPIO.setmode(GPIO.BCM)
        for pin in pin_mapping.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_active(self, direction):
        pin = self.pin_mapping[direction]
        # Joystick direction active == LOW (False)
        return not GPIO.input(pin)

    def active_directions(self):
        return [name for name, pin in self.pin_mapping.items() if not GPIO.input(pin)]

    def cleanup(self):
        GPIO.cleanup()