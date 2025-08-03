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

    def get_increment(self):
        """Return the increment value for display purposes (default: 1, overridden by AddModeHandler)."""
        return getattr(self.timer, "add_increment", 1)

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

    def get_increment(self):
        return 1  # Always 1 for display in loop mode

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

    def get_increment(self):
        return 1  # Always 1 for display in random mode

class AddModeHandler(BaseModeHandler):
    """
    "add" mode: Each time the CLOSE cycle occurs, a stable increment is added to the base close time.
    The increment can be changed at runtime (e.g. via joystick up/down) using timer.add_increment.
    This version ensures that next_time is always up to date, including after increment/base changes.
    """
    def __init__(self, timer):
        super().__init__(timer)
        self._accumulated = 0

    def initialize(self):
        # Reset accumulation when (re-)initialized
        self._accumulated = 0
        self.timer.open_time = self.timer._open_time_base
        self.timer.close_time = self.timer._close_time_base + self._accumulated
        self.set_next_time()

    def transition(self):
        if self.timer.status == "OPEN":
            self.timer.status = "CLOSE"
            # On every close cycle, increment the accumulator
            self._accumulated += self.timer.add_increment
            self.timer.close_time = self.timer.close_time_base + self._accumulated
            self.set_next_time()
        else:
            self.timer.status = "OPEN"
            self.timer.open_time = self.timer.open_time_base
            self.set_next_time()

    def set_next_time(self):
        if self.timer.status == "OPEN":
            # Next will be a CLOSE, show what the next close time will be if increment is applied
            next_accum = self._accumulated + self.timer.add_increment
            self.timer.next_time = self.timer.close_time_base + next_accum
        else:
            # Next will be an OPEN, always base open time
            self.timer.next_time = self.timer.open_time_base

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = max(1, int(self.timer._open_time_base) + int(delta))
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
        self.set_next_time()  # Update next_time to reflect new base values

    def update_increment(self):
        # Call this after changing add_increment externally (e.g. via joystick)
        self.set_next_time()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

    def randomize_if_needed(self):
        self.initialize()

    def get_increment(self):
        return self.timer.add_increment  # Show the current, user-changable increment