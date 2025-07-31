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

    def setmode(self, mode):
        self._mode = mode
        logger.debug(f"Mock GPIO: setmode({mode})")

    def setup(self, pin, mode, pull_up_down=None):
        self._pins[pin] = {'mode': mode, 'pull': pull_up_down, 'state': self.HIGH}
        logger.debug(f"Mock GPIO: setup(pin={pin}, mode={mode}, pull_up_down={pull_up_down})")

    def input(self, pin):
        # Always return the current state (default HIGH if not set up)
        state = self._pins.get(pin, {}).get('state', self.HIGH)
        return state

    def output(self, pin, state):
        if pin not in self._pins:
            raise RuntimeError(f"Pin {pin} not set up")
        self._pins[pin]['state'] = state
        logger.debug(f"Mock GPIO: output(pin={pin}, state={state})")

    def cleanup(self):
        logger.debug("Mock GPIO: cleanup()")
        self._pins.clear()

    # Helpers for test/GUI
    def _press(self, pin):
        if pin not in self._pins:
            self._pins[pin] = {'mode': self.IN, 'pull': self.PUD_UP, 'state': self.HIGH}
        self._pins[pin]['state'] = self.LOW
        logger.debug(f"Mock GPIO: _press(pin={pin}) (state=LOW)")

    def _release(self, pin):
        if pin not in self._pins:
            self._pins[pin] = {'mode': self.IN, 'pull': self.PUD_UP, 'state': self.HIGH}
        self._pins[pin]['state'] = self.HIGH
        logger.debug(f"Mock GPIO: _release(pin={pin}) (state=HIGH)")

GPIO = GPIOClass()