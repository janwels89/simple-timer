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

class Output:
    """
    Class to control two output GPIO pins (relays, LEDs, etc.) on a Raspberry Pi.
    Example usage:
        out = Output()
        out.set_state(1, True)  # Turn relay 1 ON
        out.set_state(2, False) # Turn relay 2 OFF
        out.cleanup()
    """
    # GPIO pins for the outputs (change if you want different pins)
    _pin_mapping = {
        1: 4,   # Output 1 on GPIO4
        2: 17,  # Output 2 on GPIO17
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self._pin_mapping.values():
            GPIO.setup(pin, GPIO.OUT)
        # Optional: set initial state (both OFF, i.e. HIGH for active LOW relay)
        for pin in self._pin_mapping.values():
            GPIO.output(pin, GPIO.HIGH)

    def set_state(self, output_number, state):
        """
        Set the state of an output.
        output_number: 1 or 2
        state: True (ON) or False (OFF)
        For most relay modules (active LOW):
            - ON  -> GPIO.LOW (relay energizes, click)
            - OFF -> GPIO.HIGH (relay de-energizes)
        """
        pin = self._pin_mapping.get(output_number)
        if pin is None:
            raise ValueError(f"Invalid output number: {output_number}")
        # Active LOW logic: relay activates when pin is LOW
        GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)

    def get_state(self, output_number):
        """
        Get the state of an output.
        Returns: True if ON (relay energized, GPIO LOW), False if OFF (GPIO HIGH)
        """
        pin = self._pin_mapping.get(output_number)
        if pin is None:
            raise ValueError(f"Invalid output number: {output_number}")
        return GPIO.input(pin) == GPIO.LOW  # True means relay should be ON

    def cleanup(self):
        GPIO.cleanup()