# Timer Logic (Loop Timing, state)

class TimerController:
    def __init__(self):
        self.on_time = 5
        self.off_time = 5
        self.mode = "ON"   # "ON" or "OFF"
        self.enabled = False

    def increase_time(self):
        if self.mode == "ON":
            self.on_time += 1
        elif self.mode == "OFF":
            self.off_time += 1

    def decrease_time(self):
        if self.mode == "ON":
            self.on_time = max(1, self.on_time - 1)
        elif self.mode == "OFF":
            self.off_time = max(1, self.off_time - 1)