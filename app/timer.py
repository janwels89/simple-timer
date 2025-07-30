import time
import os
import json
import logging

SETTINGS_FILE = "settings.json"

logger = logging.getLogger(__name__)

class TimerController:
    DEFAULT_OPEN_TIME = 5
    DEFAULT_CLOSE_TIME = 5

    def __init__(self):
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self.status = "OPEN"
        self.mode = "loop"
        self.enabled = False
        self.elapsed = 0
        self.last_update_time = time.monotonic()
        self.show_zero = False
        self.load_settings()
        logger.debug(f"TimerController initialized: open={self.open_time}, close={self.close_time}, status={self.status}, mode={self.mode}")

    def update(self):
        logger.debug(f"Update called. enabled={self.enabled}, status={self.status}, elapsed={self.elapsed}, show_zero={self.show_zero}")
        if not self.enabled:
            logger.debug("Timer is not enabled. Skipping update.")
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        logger.debug(f"Time since last update: {delta:.3f} seconds")
        self.last_update_time = now

        time_left = delta
        while time_left > 0:
            if self.show_zero:
                logger.debug("Display is showing zero. Switching timer state.")
                self.show_zero = False
                self.elapsed = 0
                self.status = "CLOSE" if self.status == "OPEN" else "OPEN"
                logger.debug(f"Timer switched to {self.status}. Timer reset.")
                break

            if self.status == "OPEN":
                remaining = self.open_time - self.elapsed
            else:
                remaining = self.close_time - self.elapsed

            logger.debug(f"Time remaining in current state ({self.status}): {remaining:.3f} seconds")
            if remaining > 0:
                if time_left >= remaining:
                    self.elapsed += remaining
                    time_left -= remaining
                    self.show_zero = True
                    logger.debug("Timer reached zero. Will show zero next tick.")
                    break
                else:
                    self.elapsed += time_left
                    logger.debug(f"Timer incremented by {time_left:.3f} seconds, now elapsed={self.elapsed:.3f}")
                    time_left = 0
            else:
                self.show_zero = True
                logger.debug("Remaining time is zero or less, setting show_zero.")
                break

    def adjust_time(self, delta):
        logger.debug(f"Adjusting time: delta={delta}, current status={self.status}")
        if self.status == "OPEN":
            self.open_time = max(0, self.open_time + delta)
            logger.debug(f"OPEN time adjusted to {self.open_time}")
        elif self.status == "CLOSE":
            self.close_time = max(0, self.close_time + delta)
            logger.debug(f"CLOSE time adjusted to {self.close_time}")
        else:
            logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
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
        logger.debug(f"Timer settings saved: {data}")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.open_time = int(data.get("open_time", self.DEFAULT_OPEN_TIME))
                    self.close_time = int(data.get("close_time", self.DEFAULT_CLOSE_TIME))
                logger.debug(f"Timer settings loaded: open_time={self.open_time}, close_time={self.close_time}")
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to load timer settings, using defaults. Error: {e}")
                self.open_time = self.DEFAULT_OPEN_TIME
                self.close_time = self.DEFAULT_CLOSE_TIME
        else:
            self.open_time = self.DEFAULT_OPEN_TIME
            self.close_time = self.DEFAULT_CLOSE_TIME
            logger.debug("No settings file found. Using default times.")

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
