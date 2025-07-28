# Timer Logic (Loop Timing, state)

class TimerController:
    def __init__(self):
        self.on_time = 5
        self.off_time = 5
        self.mode = None
        self.enabled = True
        self.elapsed = 0


    def adjust_time(self, delta):
        if self.mode == "ON":
                self.on_time = max(1, self.on_time + delta)
        elif self.mode == "OFF":
                self.off_time = max(1, self.off_time + delta)
        else:
            raise ValueError("Timer mode must be 'ON' or 'OFF'")


    def increase_time(self):
        self.adjust_time(+1)


    def decrease_time(self):
        self.adjust_time(-1)

    def advance_time(self, seconds):
        if not self.enabled:
            return

        time_left = seconds

        while time_left > 0:
            if self.mode == "ON":
                remaining = self.on_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.mode = "OFF"
                    self.elapsed = 0
                else:
                    self.elapsed += time_left
                    time_left = 0
            else:  # OFF mode
                remaining = self.off_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.mode = "ON"
                    self.elapsed = 0
                else:
                    self.elapsed += time_left
                    time_left = 0