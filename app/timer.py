import time
import json
import os

SETTINGS_FILE = "timer_settings.json"

class TimerController:
    DEFAULT_OPEN_TIME = 5
    DEFAULT_CLOSE_TIME = 5

    def __init__(self):
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self.status = "OPEN"  # default OPEN
        self.mode = "loop"
        self.enabled = True
        self.elapsed = 0
        self.last_update_time = time.monotonic()  # for real-time ticking
        self.load_settings()

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

    def advance_time(self, seconds):
        """Testable, manual time simulatiOPEN"""
        if not self.enabled:
            return

        time_left = seconds

        while time_left > 0:
            if self.status == "OPEN":
                remaining = self.open_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.status = "CLOSE"
                    self.elapsed = 0
                else:
                    self.elapsed += time_left
                    time_left = 0
            else:  # CLOSE
                remaining = self.close_time - self.elapsed
                if time_left >= remaining:
                    time_left -= remaining
                    self.status = "OPEN"
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

    def save_settings(self):
        data = {
            "open_time": self.open_time,
            "close_time": self.close_time
        }
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
                # If file is corrupted, use defaults
                self.open_time = self.DEFAULT_OPEN_TIME
                self.close_time = self.DEFAULT_CLOSE_TIME


    def reset_settings(self):
        """Delete the settings file and reset to defaults."""
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)