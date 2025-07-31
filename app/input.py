import os
import platform
import logging

logger = logging.getLogger(__name__)

def _get_gpio_module():
    gpio_type = os.getenv("GPIO_DRIVER")
    if gpio_type == "mock":
        from features.steps.mocks.mock_gpio import GPIO
        logger.debug("Using MOCK GPIO (forced by GPIO_DRIVER=mock)")
        return GPIO
    elif gpio_type == "real":
        import RPi.GPIO as GPIO
        logger.debug("Using REAL GPIO (forced by GPIO_DRIVER=real)")
        return GPIO
    else:
        arch = platform.machine().lower()
        if any(arm in arch for arm in ("arm", "aarch64")):
            import RPi.GPIO as GPIO
            logger.debug("Using REAL GPIO (platform is ARM)")
            return GPIO
        else:
            from features.steps.mocks.mock_gpio import GPIO
            logger.debug("Using MOCK GPIO (platform is NOT ARM)")
            return GPIO

GPIO = _get_gpio_module()


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
        self._last_pressed = set()

    def is_pressed(self, key_name):
        pin = self._pin_mapping.get(key_name)
        if pin is None:
            raise ValueError(f"Unknown button: {key_name}")
        return GPIO.input(pin) == GPIO.LOW

    def pressed_buttons(self):
        current_pressed = {name for name, pin in self._pin_mapping.items() if GPIO.input(pin) == GPIO.LOW}
        if current_pressed != self._last_pressed:
            logger.debug(f"Button state changed: pressed={sorted(current_pressed)}")
            self._last_pressed = current_pressed.copy()
        return list(current_pressed)

    def cleanup(self):
        GPIO.cleanup()


class JoystickInput:
    """
    Handles 5-way joystick for Waveshare 1.3inch OLED HAT.
    Directions: 'up', 'down', 'left', 'right', 'press'
    BCM Pin mapping:
      up: 6
      down: 19
      left: 5
      right: 26
      press: 13
    """
    _pin_mapping = {
        "up": 19,
        "down": 6,
        "left": 5,
        "right": 26,
        "press": 13,
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self._pin_mapping.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._last_active = set()

    def is_active(self, direction):
        """
        Returns True if the specified direction is currently pressed.
        direction: one of 'up', 'down', 'left', 'right', 'press'
        """
        pin = self._pin_mapping.get(direction)
        if pin is None:
            raise ValueError(f"Unknown joystick direction: {direction}")
        return GPIO.input(pin) == GPIO.LOW

    def active_directions(self):
        """
        Returns a list of all currently pressed directions.
        """
        current_active = {name for name, pin in self._pin_mapping.items() if GPIO.input(pin) == GPIO.LOW}
        if current_active != self._last_active:
            logger.debug(f"Joystick state changed: active={sorted(current_active)}")
            self._last_active = current_active.copy()
        return list(current_active)

    def cleanup(self):
        GPIO.cleanup()