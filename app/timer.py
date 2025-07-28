# Timer Logic (Loop Timing, state)

class TimerController:
    def __init__(self):
        self.on_time = 5
        self.off_time = 5
        self.mode = None
        self.enabled = True


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

