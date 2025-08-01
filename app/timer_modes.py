import random

class BaseModeHandler:
    def __init__(self, timer):
        self.timer = timer

    def initialize(self):
        """Set up the timer for this mode (called after mode switch or settings load)."""
        raise NotImplementedError

    def transition(self):
        raise NotImplementedError

    def set_next_time(self):
        raise NotImplementedError

    def adjust_time(self, delta):
        raise NotImplementedError

    def current_remaining_time(self):
        """Return the remaining time in the current state."""
        raise NotImplementedError

    def randomize_if_needed(self):
        # Default: do nothing. Overridden by RandomModeHandler.
        pass

class LoopModeHandler(BaseModeHandler):
    def initialize(self):
        # Always set times to base values in loop mode
        self.timer.open_time = self.timer._open_time_base
        self.timer.close_time = self.timer._close_time_base
        self.set_next_time()

    def transition(self):
        if self.timer.status == "OPEN":
            self.timer.status = "CLOSE"
            self.timer.close_time = self.timer.close_time_base
            self.timer.next_time = self.timer.open_time_base
        else:
            self.timer.status = "OPEN"
            self.timer.open_time = self.timer.open_time_base
            self.timer.next_time = self.timer.close_time_base

    def set_next_time(self):
        if self.timer.status == "OPEN":
            self.timer.next_time = self.timer.close_time_base
        else:
            self.timer.next_time = self.timer.open_time_base

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = max(1, int(self.timer._open_time_base) + int(delta))
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
        self.initialize()  # Re-initialize to update times

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

class RandomModeHandler(BaseModeHandler):
    def initialize(self):
        # Randomize both periods for entry to random mode
        if self.timer.status == "OPEN":
            self.timer.open_time = self._random_period("OPEN")
            self.timer.next_time = self._random_period("CLOSE")
        else:
            self.timer.close_time = self._random_period("CLOSE")
            self.timer.next_time = self._random_period("OPEN")

    def _random_period(self, period):
        base = self.timer._open_time_base if period == "OPEN" else self.timer._close_time_base
        return random.randint(1, max(1, int(base)))

    def transition(self):
        if self.timer.status == "OPEN":
            self.timer.status = "CLOSE"
            self.timer.close_time = self.timer.next_time  # use previously randomized close period
            self.timer.next_time = self._random_period("OPEN")  # randomize next open period
        else:
            self.timer.status = "OPEN"
            self.timer.open_time = self.timer.next_time   # use previously randomized open period
            self.timer.next_time = self._random_period("CLOSE")  # randomize next close period

    def set_next_time(self):
        # Randomize only next period
        if self.timer.status == "OPEN":
            self.timer.next_time = self._random_period("CLOSE")
        else:
            self.timer.next_time = self._random_period("OPEN")

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = max(1, int(self.timer._open_time_base) + int(delta))
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
        self.set_next_time()

    def randomize_if_needed(self):
        self.initialize()  # For convenience, just call initialize

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed