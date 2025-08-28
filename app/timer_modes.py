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
        return (self.timer.open_time if self.timer.status == "OPEN" else self.timer.close_time) - self.timer.elapsed

    def get_increment(self):
        return 1


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
            self.timer.next_time = self._random_period("CLOSE")
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
            self.timer.next_time = self._random_period("OPEN")

    def randomize_if_needed(self):
        self.set_next_time()

    def current_remaining_time(self):
        return (self.timer.open_time if self.timer.status == "OPEN" else self.timer.close_time) - self.timer.elapsed

    def get_increment(self):
        return 1


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
            if not self._reset_next:
                self._accumulated += self.timer.add_increment
                self.timer.status = "OPEN"
                self._update_times()
                self.set_next_time()
            else:
                self.transition()


    def set_next_time(self):
        if self._reset_next and self.timer.status == "CLOSE":
            self.timer.next_time = self.timer.open_time_base
        elif self.timer.status == "OPEN":
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

    def current_remaining_time(self):
        return (self.timer.open_time if self.timer.status == "OPEN" else self.timer.close_time) - self.timer.elapsed

    def randomize_if_needed(self):
        self.initialize()

    def get_increment(self):
        return self.timer.add_increment

    def get_status_b(self):
        return f"inc: {self.timer.add_increment}"


class AddSubModeHandler(BaseModeHandler):
    """
    AddSubModeHandler ('no negative open, skip long close, always in sync'):
    - Each CLOSE cycle, subtract increment from open and add to close.
    - If open_time would be zero or negative, immediately reset to base and start with OPEN (no CLOSE with negative open).
    """
    def __init__(self, timer):
        super().__init__(timer)
        self._accumulated = 0

    def initialize(self):
        self._accumulated = 0
        self._reset_to_base()
        self.timer.status = "OPEN"
        self.set_next_time()

    def _reset_to_base(self):
        self.timer.open_time = self.timer._open_time_base
        self.timer.close_time = self.timer._close_time_base

    def _update_times(self):
        self.timer.open_time = self.timer._open_time_base - self._accumulated * self.timer.add_increment
        self.timer.close_time = self.timer._close_time_base + self._accumulated * self.timer.add_increment

    def transition(self):
        if self.timer.status == "OPEN":
            next_open = self.timer._open_time_base - (self._accumulated + 1) * self.timer.add_increment
            if next_open < 1:
                self._accumulated = 0
                self._reset_to_base()
                self.timer.status = "OPEN"
                self.set_next_time()
                return
            self.timer.status = "CLOSE"
            self._update_times()
            self.set_next_time()
        else:
            self._accumulated += 1
            self.timer.status = "OPEN"
            self._update_times()
            self.set_next_time()

    def set_next_time(self):
        if self.timer.status == "OPEN":
            self.timer.next_time = self.timer._close_time_base + self._accumulated * self.timer.add_increment
        else:
            self.timer.next_time = self.timer._open_time_base - (self._accumulated + 1) * self.timer.add_increment

    def adjust_time(self, delta):
        if self.timer.status == "OPEN":
            self.timer._open_time_base = max(1, int(self.timer._open_time_base) + int(delta))
        else:
            self.timer._close_time_base = max(1, int(self.timer._close_time_base) + int(delta))
        self.set_next_time()

    def adjust(self, direction):
        self.timer.add_increment = max(1, self.timer.add_increment + direction)
        self.set_next_time()

    def current_remaining_time(self):
        if self.timer.status == "OPEN":
            return max(0, base - self.timer.elapsed)
        else:
            return base - self.timer.elapsed

    def randomize_if_needed(self):
        self.initialize()

    def get_increment(self):
        return self.timer.add_increment

    def get_status_b(self):
        return f"inc: {self.timer.add_increment}"

