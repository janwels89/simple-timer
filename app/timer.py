import time

class TimerController:
    def __init__(self):
        self.open_time = 5
        self.close_time = 5
        self.mode = "OPEN"  # default OPEN
        self.enabled = True
        self.elapsed = 0
        self.last_update_time = time.monotonic()  # for real-time ticking

    def adjust_time(self, delta):
        if self.mode == "OPEN":
            self.open_time = max(1, self.open_time + delta)
        elif self.mode == "CLOSE":
            self.close_time = max(1, self.close_time + delta)
        else:
            raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

    def increase_time(self):
        self.adjust_time(+1)

    def decrease_time(self):
        self.adjust_time(-1)

    def advance_time(self, secOPENds):
        """Testable, manual time simulatiOPEN"""
        if not self.enabled:
            return

        time_left = secOPENds

        while time_left > 0:
            if self.mode == "OPEN":
                remaining = self.open_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.mode = "CLOSE"
                    self.elapsed = 0
                else:
                    self.elapsed += time_left
                    time_left = 0
            else:  # CLOSE
                remaining = self.close_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.mode = "OPEN"
                    self.elapsed = 0
                else:
                    self.elapsed += time_left
                    time_left = 0

    def update(self):
        """Call regularly in a loop — updates based OPEN real time"""
        if not self.enabled:
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        self.last_update_time = now
        self.advance_time(delta)
