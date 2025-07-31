import logging

logger = logging.getLogger(__name__)

class GPIOClass:
    BCM = 'BCM'
    BOARD = 'BOARD'
    IN = 'IN'
    OUT = 'OUT'
    PUD_UP = 'PUD_UP'
    PUD_DOWN = 'PUD_DOWN'
    LOW = 0
    HIGH = 1

    def __init__(self):
        self._mode = None
        self._pins = {}
        self._key2_pressed = False
        self._key2_pin = 20  # BCM pin for KEY2 (update if different for your board)

    def setmode(self, mode):
        self._mode = mode
        logger.debug(f"Mock GPIO: setmode({mode})")

    def setup(self, pin, mode, pull_up_down=None):
        self._pins[pin] = {'mode': mode, 'pull': pull_up_down, 'state': self.HIGH}
        logger.debug(f"Mock GPIO: setup(pin={pin}, mode={mode}, pull_up_down={pull_up_down})")

    def input(self, pin):
        # Only KEY2 is pressed once at the start, then released
        if pin == self._key2_pin and not self._key2_pressed:
            self._key2_pressed = True
            logger.debug("Mock GPIO: KEY2 is pressed (LOW) for timer start.")
            return self.LOW
        logger.debug(f"Mock GPIO: input(pin={pin}) -> {self._pins.get(pin, {}).get('state', self.HIGH)}")
        return self.HIGH

    def output(self, pin, state):
        if pin not in self._pins:
            raise RuntimeError(f"Pin {pin} not set up")
        self._pins[pin]['state'] = state
        logger.debug(f"Mock GPIO: output(pin={pin}, state={state})")

    def cleanup(self):
        logger.debug("Mock GPIO: cleanup()")
        self._pins.clear()
        self._key2_pressed = False

    # Test helpers (optional, not used for your main requirement)
    def _press(self, pin):
        if pin in self._pins:
            self._pins[pin]['state'] = self.LOW

    def _release(self, pin):
        if pin in self._pins:
            self._pins[pin]['state'] = self.HIGH

GPIO = GPIOClass()