import RPi.GPIO as GPIO

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
        # Optional: set initial state (both OFF)
        for pin in self._pin_mapping.values():
            GPIO.output(pin, GPIO.LOW)

    def set_state(self, output_number, state):
        """
        Set the state of an output.
        output_number: 1 or 2
        state: True (ON) or False (OFF)
        """
        pin = self._pin_mapping.get(output_number)
        if pin is None:
            raise ValueError(f"Invalid output number: {output_number}")
        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

    def get_state(self, output_number):
        """
        Get the state of an output.
        Returns: True if ON (HIGH), False if OFF (LOW)
        """
        pin = self._pin_mapping.get(output_number)
        if pin is None:
            raise ValueError(f"Invalid output number: {output_number}")
        return GPIO.input(pin) == GPIO.HIGH

    def cleanup(self):
        GPIO.cleanup()