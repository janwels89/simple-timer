import RPi.GPIO as GPIO

class ButtonInput:
    """
    Handles KEY1, KEY2, KEY3 for Waveshare 1.3inch OLED HAT.
    Call is_pressed('KEY1'), is_pressed('KEY2'), is_pressed('KEY3').
    """
    # Correct pin mapping for Waveshare 1.3inch OLED HAT
    _pin_mapping = {
        "KEY1": 21,
        "KEY2": 20,
        "KEY3": 16,
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