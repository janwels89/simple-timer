import random

class BaseModeHandler:
    def __init__(self, timer):
        self.timer = timer

    def initialize(self):
        raise NotImplementedError

    def transition(self):
        raise NotImplementedError

    def set_next_time(self):
        raise NotImplementedError

    def adjust_time(self, delta):
        raise NotImplementedError

    def adjust(self, direction):
        """Handle up/down joystick input for this mode. Override in add/addsub."""
        pass

    def current_remaining_time(self):
        raise NotImplementedError

    def randomize_if_needed(self):
        pass

    def get_increment(self):
        return getattr(self.timer, "add_increment", 1)

    def get_status_b(self):
        return ""


class LoopModeHandler(BaseModeHandler):
    def initialize(self):
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
        self.initialize()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

    def get_increment(self):
        return 1

    def get_status_b(self):
        return ""


class RandomModeHandler(BaseModeHandler):
    def initialize(self):
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
            self.timer.close_time = self.timer.next_time
            self.timer.next_time = self._random_period("OPEN")
        else:
            self.timer.status = "OPEN"
            self.timer.open_time = self.timer.next_time
            self.timer.next_time = self._random_period("CLOSE")

    def set_next_time(self):
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
        self.initialize()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

    def get_increment(self):
        return 1

    def get_status_b(self):
        return ""


class AddModeHandler(BaseModeHandler):
    """
    'add' mode: Each time the CLOSE cycle occurs, a stable increment is added to the base close time,
    but the increment is only applied after the first cycle.
    """
    def __init__(self, timer):
        super().__init__(timer)
        self._accumulated = 0
        self._first_cycle = True
        self._reset_next = False

    def initialize(self):
        self._accumulated = 0
        self._first_cycle = True
        self._reset_next = False
        self._update_times()
        self.set_next_time()

    def _update_times(self):
        self.timer.open_time = self.timer._open_time_base
        self.timer.close_time = self.timer._close_time_base + self._accumulated

    def transition(self):
        if self._reset_next:
            self._accumulated = 0
            self._first_cycle = True
            self._reset_next = False
            self.timer.status = "OPEN"
            self._update_times()
            self.set_next_time()
            return

        if self.timer.status == "OPEN":
            # On entering CLOSE, increment for this cycle
            if not self._first_cycle:
                self._accumulated += self.timer.add_increment
            else:
                self._first_cycle = False
            self.timer.status = "CLOSE"
            self._update_times()
            self.set_next_time()
        else:
            self.timer.status = "OPEN"
            self._update_times()
            self.set_next_time()

    def set_next_time(self):
        if self._reset_next and self.timer.status == "CLOSE":
            self.timer.next_time = self.timer.open_time_base
        elif self.timer.status == "OPEN":
            # Next is CLOSE, show what the next close time will be if increment is applied
            next_accum = self._accumulated + (0 if self._first_cycle else self.timer.add_increment)
            self.timer.next_time = self.timer.close_time_base + next_accum
        else:
            self.timer.next_time = self.timer.open_time_base

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = max(1, int(self.timer._open_time_base) + int(delta))
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
        self.set_next_time()

    def adjust(self, direction):
        self.timer.add_increment = max(1, self.timer.add_increment + direction)
        self.set_next_time()

    def update_increment(self):
        self.set_next_time()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

    def randomize_if_needed(self):
        self.initialize()

    def get_increment(self):
        return self.timer.add_increment

    def get_status_b(self):
        return f"inc: {self.timer.add_increment}"


class AddSubModeHandler(BaseModeHandler):
    """
    On every CLOSE cycle, subtract the increment from open time and add it to close time.
    If open time reaches zero or less, run OPEN with that time, then one CLOSE, then reset and start again.
    close_time is allowed to go to zero or negative.
    The increment is applied after each CLOSE, except the last one before reset.
    """
    def __init__(self, timer):
        super().__init__(timer)
        self._accumulated = 0
        self._reset_next = False

    def initialize(self):
        self._accumulated = 0
        self._reset_next = False
        self._update_times()
        self.set_next_time()

    def _update_times(self):
        open_time = self.timer._open_time_base - self._accumulated * self.timer.add_increment
        close_time = self.timer._close_time_base + self._accumulated * self.timer.add_increment
        self.timer.open_time = open_time
        self.timer.close_time = close_time

    def transition(self):
        if self._reset_next:
            # Reset everything and start again
            self._accumulated = 0
            self._reset_next = False
            self.timer.status = "OPEN"
            self._update_times()
            self.set_next_time()
            return

        if self.timer.status == "OPEN":
            if self.timer.open_time <= 0:
                self._reset_next = True
            self.timer.status = "CLOSE"
            self._update_times()
            self.set_next_time()
        else:
            # Only increment if not about to reset
            if not self._reset_next:
                self._accumulated += 1
            self.timer.status = "OPEN"
            self._update_times()
            self.set_next_time()

    def set_next_time(self):
        if self._reset_next and self.timer.status == "CLOSE":
            self.timer.next_time = self.timer.open_time_base
        elif self.timer.status == "OPEN":
            # Next is CLOSE: use current _accumulated, not pre-incremented
            next_accum = self._accumulated
            self.timer.next_time = self.timer.close_time_base + next_accum * self.timer.add_increment
        else:
            # Next is OPEN: if next will be a reset, show base
            next_accum = self._accumulated + 1 if not self._reset_next else 0
            self.timer.next_time = self.timer.open_time_base - next_accum * self.timer.add_increment

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = int(self.timer._open_time_base) + int(delta)
        else:
            self.timer._close_time_base = int(self.timer._close_time_base) + int(delta)
        self.set_next_time()

    def adjust(self, direction):
        self.timer.add_increment = max(1, self.timer.add_increment + direction)
        self.set_next_time()

    def update_increment(self):
        self.set_next_time()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return self.timer.open_time - self.timer.elapsed
        else:
            return self.timer.close_time - self.timer.elapsed

    def randomize_if_needed(self):
        self.initialize()

    def get_increment(self):
        return self.timer.add_increment

    def get_status_b(self):
        return f"inc: {self.timer.add_increment}"