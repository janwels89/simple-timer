import time
import os
import json

SETTINGS_FILE = "settings.json"

class TimerController:
    DEFAULT_OPEN_TIME = 5
    DEFAULT_CLOSE_TIME = 5

    def __init__(self):
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self.status = "OPEN"
        self.mode = "loop"
        self.enabled = True
        self.elapsed = 0
        self.last_update_time = time.monotonic()
        self.show_zero = False
        self.load_settings()

    def update(self):
        if not self.enabled:
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        self.last_update_time = now

        time_left = delta
        while time_left > 0:
            if self.show_zero:
                # Just showed 0, now switch state and reset timer
                self.show_zero = False
                self.elapsed = 0
                self.status = "CLOSE" if self.status == "OPEN" else "OPEN"
                # continue to handle time_left for the new state
                continue

            if self.status == "OPEN":
                remaining = self.open_time - self.elapsed
            else:
                remaining = self.close_time - self.elapsed

            if remaining > 0:
                if time_left >= remaining:
                    self.elapsed += remaining
                    time_left -= remaining
                    self.show_zero = True  # will display 0 next
                    # break so UI can show 0 before switching state
                    break
                else:
                    self.elapsed += time_left
                    time_left = 0
            else:
                # If remaining already 0, immediately show zero for next tick
                self.show_zero = True

    def adjust_time(self, delta):
        if self.status == "OPEN":
            self.open_time = max(0, self.open_time + delta)
        elif self.status == "CLOSE":
            self.close_time = max(0, self.close_time + delta)
        else:
            raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")
        self.save_settings()

    def increase_time(self):
        self.adjust_time(+1)

    def decrease_time(self):
        self.adjust_time(-1)

    def save_settings(self):
        data = {"open_time": self.open_time, "close_time": self.close_time}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.open_time = int(data.get("open_time", self.DEFAULT_OPEN_TIME))
                    self.close_time = int(data.get("close_time", self.DEFAULT_CLOSE_TIME))
            except (FileNotFoundError, json.JSONDecodeError, ValueError):
                self.open_time = self.DEFAULT_OPEN_TIME
                self.close_time = self.DEFAULT_CLOSE_TIME

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self.save_settings()