import time
import os
import json
import logging
import random


SETTINGS_FILE = "settings.json"

logger = logging.getLogger(__name__)

class TimerController:
    DEFAULT_OPEN_TIME = 5
    DEFAULT_CLOSE_TIME = 5

    def __init__(self):
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        # Base times store the original configured values
        self.open_time_base = self.DEFAULT_OPEN_TIME
        self.close_time_base = self.DEFAULT_CLOSE_TIME
        self.status = "OPEN"
        self.mode = "loop"
        self.enabled = False
        self.elapsed = 0
        self.last_update_time = time.monotonic()
        self.show_zero = False
        self._last_state = {}
        self.load_settings()
        logger.debug(f"TimerController initialized: open={self.open_time}, close={self.close_time}, status={self.status}, mode={self.mode}")

    def randomize_if_needed(self):
        """Randomize timer values if in random mode"""
        if self.mode == "random":
            # In random mode, randomize both values
            self.open_time = random.randint(0, self.open_time_base)
            self.close_time = random.randint(0, self.close_time_base)
            logger.debug(f"Randomized: open={self.open_time}/{self.open_time_base}, close={self.close_time}/{self.close_time_base}")
        else:
            # In loop mode, use base values
            self.open_time = self.open_time_base
            self.close_time = self.close_time_base

    def toggle_random_mode(self):
        """Toggle between random and loop mode"""
        if self.mode == "random":
            self.mode = "loop"
        else:
            self.mode = "random"
        self.randomize_if_needed()
        logger.info(f"Toggled to {self.mode} mode")

    def _log_state_change(self):
        state = {
            "open_time": self.open_time,
            "close_time": self.close_time,
            "status": self.status,
            "enabled": self.enabled,
            "elapsed": round(self.elapsed, 3),
            "show_zero": self.show_zero,
            "mode": self.mode,
        }
        if state != self._last_state:
            logger.info(
                "Timer state changed: open_time=%s, close_time=%s, status=%s, enabled=%s, elapsed=%.3f, show_zero=%s, mode=%s",
                self.open_time, self.close_time, self.status, self.enabled, self.elapsed, self.show_zero, self.mode
            )
            self._last_state = state.copy()

    def update(self):
        prev_state = {
            "open_time": self.open_time,
            "close_time": self.close_time,
            "status": self.status,
            "enabled": self.enabled,
            "elapsed": round(self.elapsed, 3),
            "show_zero": self.show_zero,
        }
        if not self.enabled:
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        self.last_update_time = now

        time_left = delta
        while time_left > 0:
            if self.show_zero:
                self.show_zero = False
                self.elapsed = 0
                self.status = "CLOSE" if self.status == "OPEN" else "OPEN"
                # In random mode, randomize the next period's value only
                if self.mode == "random":
                    if self.status == "OPEN":
                        self.open_time = random.randint(0, self.open_time_base)
                    else:
                        self.close_time = random.randint(0, self.close_time_base)
                    logger.debug(f"Period transition - randomized {self.status}: {self.open_time if self.status == 'OPEN' else self.close_time}")
                break

            if self.status == "OPEN":
                remaining = self.open_time - self.elapsed
            else:
                remaining = self.close_time - self.elapsed

            if remaining > 0:
                if time_left >= remaining:
                    self.elapsed += remaining
                    time_left -= remaining
                    self.show_zero = True
                    break
                else:
                    self.elapsed += time_left
                    time_left = 0
            else:
                self.show_zero = True
                break

        self._log_state_change()

    def adjust_time(self, delta):
        prev_open = self.open_time_base
        prev_close = self.close_time_base
        if self.status == "OPEN":
            self.open_time_base = max(0, self.open_time_base + delta)
            # Update current value if in loop mode or if currently running OPEN
            if self.mode == "loop" or self.status == "OPEN":
                self.open_time = self.open_time_base
        elif self.status == "CLOSE":
            self.close_time_base = max(0, self.close_time_base + delta)
            # Update current value if in loop mode or if currently running CLOSE
            if self.mode == "loop" or self.status == "CLOSE":
                self.close_time = self.close_time_base
        else:
            logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
            raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")
        self.save_settings()
        if prev_open != self.open_time_base or prev_close != self.close_time_base:
            self._log_state_change()

    def increase_time(self):
        self.adjust_time(+1)

    def decrease_time(self):
        self.adjust_time(-1)

    def save_settings(self):
        data = {"open_time": self.open_time_base, "close_time": self.close_time_base}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        # Only log settings save if they actually changed (covered by state change)

    def load_settings(self):
        loaded = False
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.open_time_base = int(data.get("open_time", self.DEFAULT_OPEN_TIME))
                    self.close_time_base = int(data.get("close_time", self.DEFAULT_CLOSE_TIME))
                    # Set current values to base values initially
                    self.open_time = self.open_time_base
                    self.close_time = self.close_time_base
                loaded = True
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to load timer settings, using defaults. Error: {e}")
                self.open_time_base = self.DEFAULT_OPEN_TIME
                self.close_time_base = self.DEFAULT_CLOSE_TIME
                self.open_time = self.open_time_base
                self.close_time = self.close_time_base
        else:
            self.open_time_base = self.DEFAULT_OPEN_TIME
            self.close_time_base = self.DEFAULT_CLOSE_TIME
            self.open_time = self.open_time_base
            self.close_time = self.close_time_base

        if loaded:
            self._log_state_change()

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time_base = self.DEFAULT_OPEN_TIME
        self.close_time_base = self.DEFAULT_CLOSE_TIME
        self.open_time = self.open_time_base
        self.close_time = self.close_time_base
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
        self._log_state_change()