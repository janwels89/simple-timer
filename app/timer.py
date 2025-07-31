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
        self.status = "OPEN"
        self.mode = "loop"
        self.enabled = False
        self.elapsed = 0
        self.last_update_time = time.monotonic()
        self.show_zero = False
        self._last_state = {}
        # Base values for random mode (will be set when entering random mode)
        self._open_time_base = None
        self._close_time_base = None
        self.load_settings()
        logger.debug(f"TimerController initialized: open={self.open_time}, close={self.close_time}, status={self.status}, mode={self.mode}")

    def _log_state_change(self):
        state = {
            "open_time": self.open_time,
            "close_time": self.close_time,
            "status": self.status,
            "enabled": self.enabled,
            "elapsed": round(self.elapsed, 3),
            "show_zero": self.show_zero,
        }
        if state != self._last_state:
            logger.info(
                "Timer state changed: open_time=%s, close_time=%s, status=%s, enabled=%s, elapsed=%.3f, show_zero=%s",
                self.open_time, self.close_time, self.status, self.enabled, self.elapsed, self.show_zero
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
                # Reload base values and re-randomize on period transition
                if self.mode == "random":
                    self.load_settings()  # Reload base values from settings
                    # Set the loaded values as base values
                    if self._open_time_base is None:
                        self._open_time_base = self.open_time
                        self._close_time_base = self.close_time
                    else:
                        # Update base values from settings
                        self._open_time_base = self.open_time
                        self._close_time_base = self.close_time
                    self.randomize_if_needed()  # Apply new randomization
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
        if self.mode == "random":
            # In random mode, adjust base values
            if self._open_time_base is None:
                self._open_time_base = self.open_time
                self._close_time_base = self.close_time
            
            prev_open = self._open_time_base
            prev_close = self._close_time_base
            if self.status == "OPEN":
                self._open_time_base = max(0, self._open_time_base + delta)
            elif self.status == "CLOSE":
                self._close_time_base = max(0, self._close_time_base + delta)
            else:
                logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
                raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")
        else:
            # In loop mode, adjust current values directly
            prev_open = self.open_time
            prev_close = self.close_time
            if self.status == "OPEN":
                self.open_time = max(0, self.open_time + delta)
            elif self.status == "CLOSE":
                self.close_time = max(0, self.close_time + delta)
            else:
                logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
                raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")
        
        self.save_settings()
        if (self.mode == "random" and (prev_open != self._open_time_base or prev_close != self._close_time_base)) or \
           (self.mode != "random" and (prev_open != self.open_time or prev_close != self.close_time)):
            self._log_state_change()

    def increase_time(self):
        self.adjust_time(+1)

    def decrease_time(self):
        self.adjust_time(-1)

    def save_settings(self):
        # Save the base values if in random mode, otherwise save current values
        if self.mode == "random" and self._open_time_base is not None:
            data = {"open_time": self._open_time_base, "close_time": self._close_time_base}
        else:
            data = {"open_time": self.open_time, "close_time": self.close_time}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        # Only log settings save if they actually changed (covered by state change)

    def load_settings(self):
        loaded = False
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.open_time = int(data.get("open_time", self.DEFAULT_OPEN_TIME))
                    self.close_time = int(data.get("close_time", self.DEFAULT_CLOSE_TIME))
                loaded = True
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to load timer settings, using defaults. Error: {e}")
                self.open_time = self.DEFAULT_OPEN_TIME
                self.close_time = self.DEFAULT_CLOSE_TIME
        else:
            self.open_time = self.DEFAULT_OPEN_TIME
            self.close_time = self.DEFAULT_CLOSE_TIME

        if loaded:
            self._log_state_change()

    def randomize_if_needed(self):
        if self.mode == "random":
            if self._open_time_base is None:
                self._open_time_base = self.open_time
                self._close_time_base = self.close_time

            if self.status == "OPEN":
                # Only randomize open_time for the next OPEN period
                self.open_time = int(round(self._open_time_base * random.random()))
            elif self.status == "CLOSE":
                # Only randomize close_time for the next CLOSE period
                self.close_time = int(round(self._close_time_base * random.random()))

            # Generate random multipliers between 0 and 1
            open_multiplier = random.random()
            close_multiplier = random.random()

            # Apply randomization to base values and ensure integer result
            self.open_time = int(round(self._open_time_base * open_multiplier))
            self.close_time = int(round(self._close_time_base * close_multiplier))
            
            logger.debug(f"Randomized times: open={self.open_time:.3f} (base={self._open_time_base}), close={self.close_time:.3f} (base={self._close_time_base})")
        else:
            # Use base values directly if available, otherwise current values
            if self._open_time_base is not None:
                self.open_time = self._open_time_base
                self.close_time = self._close_time_base
                # Clear base values when exiting random mode
                self._open_time_base = None
                self._close_time_base = None
                logger.debug(f"Restored base times: open={self.open_time}, close={self.close_time}")
        
        self._log_state_change()

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self._open_time_base = None
        self._close_time_base = None
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
        self._log_state_change()