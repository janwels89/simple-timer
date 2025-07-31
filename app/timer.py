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
        self._open_time_base = None
        self._close_time_base = None
        self.next_time = None  # Single buffer for random mode
        self.load_settings()
        logger.debug(
            f"TimerController initialized: open={self.open_time}, close={self.close_time}, status={self.status}, mode={self.mode}")

    def _log_state_change(self):
        state = {
            "open_time": self.open_time,
            "close_time": self.close_time,
            "status": self.status,
            "enabled": self.enabled,
            "elapsed": round(self.elapsed, 3),
            "show_zero": self.show_zero,
            "next_time": self.next_time,
        }
        if state != self._last_state:
            logger.info(
                "Timer state changed: open_time=%s, close_time=%s, status=%s, enabled=%s, elapsed=%.3f, show_zero=%s, next_time=%s",
                self.open_time, self.close_time, self.status, self.enabled, self.elapsed, self.show_zero, self.next_time
            )
            self._last_state = state.copy()

    def _debug_random(self, msg):
        logger.debug(f"[RANDOM] {msg} | open={self.open_time}, close={self.close_time}, next_time={self.next_time}, base_open={self._open_time_base}, base_close={self._close_time_base}")

    def update(self):
        if not self.enabled:
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        self.last_update_time = now

        time_left = delta
        while time_left > 0:
            if self.show_zero:
                self._debug_random(f"Transition ({self.status}→{'CLOSE' if self.status == 'OPEN' else 'OPEN'}) - BEFORE")
                self.show_zero = False
                self.elapsed = 0
                if self.status == "OPEN":
                    self.status = "CLOSE"
                    if self.mode == "random":
                        self.close_time = self.next_time
                        self._debug_random("Assigned close_time from next_time (transition to CLOSE)")
                        self.next_time = self._random_period("OPEN")
                        self._debug_random("Randomized next_time (for next OPEN)")
                    else:
                        self.close_time = self._close_time_base if self._close_time_base is not None else self.DEFAULT_CLOSE_TIME
                else:  # was CLOSE, now OPEN
                    self.status = "OPEN"
                    if self.mode == "random":
                        self.open_time = self.next_time
                        self._debug_random("Assigned open_time from next_time (transition to OPEN)")
                        self.next_time = self._random_period("CLOSE")
                        self._debug_random("Randomized next_time (for next CLOSE)")
                    else:
                        self.open_time = self._open_time_base if self._open_time_base is not None else self.DEFAULT_OPEN_TIME
                self._debug_random(f"Transition ({self.status}) - AFTER")
                self._log_state_change()
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

    def adjust_time(self, delta):
        if self.mode == "random":
            if self._open_time_base is None:
                self._open_time_base = self.open_time
            if self._close_time_base is None:
                self._close_time_base = self.close_time

            prev_open = self._open_time_base
            prev_close = self._close_time_base
            if self.status == "OPEN":
                self._open_time_base = max(1, self._open_time_base + delta)
                self._debug_random(f"Adjusted open_time_base by {delta}")
                # Only update next_time if we're about to enter OPEN next
                if self.status == "CLOSE":
                    self.next_time = self._random_period("OPEN")
                    self._debug_random("Randomized next_time (for next OPEN)")
            elif self.status == "CLOSE":
                self._close_time_base = max(1, self._close_time_base + delta)
                self._debug_random(f"Adjusted close_time_base by {delta}")
                if self.status == "OPEN":
                    self.next_time = self._random_period("CLOSE")
                    self._debug_random("Randomized next_time (for next CLOSE)")
            else:
                logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
                raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")
        else:
            prev_open = self.open_time
            prev_close = self.close_time
            if self.status == "OPEN":
                self.open_time = max(1, self.open_time + delta)
            elif self.status == "CLOSE":
                self.close_time = max(1, self.close_time + delta)
            else:
                logger.error("Timer mode must be 'OPEN' or 'CLOSE'")
                raise ValueError("Timer mode must be 'OPEN' or 'CLOSE'")

        self.save_settings()
        if (self.mode == "random" and (prev_open != self._open_time_base or prev_close != self._close_time_base)) or \
                (self.mode != "random" and (prev_open != self.open_time or prev_close != self.close_time)):
            self._log_state_change()

    def _random_period(self, period):
        base = self._open_time_base if period == "OPEN" else self._close_time_base
        if base is None:
            base = self.DEFAULT_OPEN_TIME if period == "OPEN" else self.DEFAULT_CLOSE_TIME
        val = max(1, int(round(random.uniform(base * 0.5, base))))
        logger.debug(f"[RANDOM] _random_period({period}) returns {val} (base={base})")
        return val

    def save_settings(self):
        if self.mode == "random" and self._open_time_base is not None:
            data = {"open_time": self._open_time_base, "close_time": self._close_time_base}
        else:
            data = {"open_time": self.open_time, "close_time": self.close_time}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

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

        if self.mode == "random":
            self._open_time_base = self.open_time
            self._close_time_base = self.close_time
            if self.status == "OPEN":
                self.open_time = self._random_period("OPEN")
                self.next_time = self._random_period("CLOSE")
            else:
                self.close_time = self._random_period("CLOSE")
                self.next_time = self._random_period("OPEN")
            self._debug_random("Loaded settings in random mode")
        if loaded:
            self._log_state_change()

    def randomize_if_needed(self):
        if self.mode == "random":
            # Initialize base values if missing
            if self._open_time_base is None:
                self._open_time_base = self.open_time
            if self._close_time_base is None:
                self._close_time_base = self.close_time

            # Always randomize both periods on entering random mode
            self.open_time = self._random_period("OPEN")
            self.close_time = self._random_period("CLOSE")
            # Set the buffer for the next period (not the current one)
            if self.status == "OPEN":
                # Currently OPEN, so next period will be CLOSE
                self.next_time = self.close_time
            else:
                # Currently CLOSE, so next period will be OPEN
                self.next_time = self.open_time

            self._debug_random("Randomized both periods for random mode entry")
        else:
            # Restore fixed values and clear random state
            if self._open_time_base is not None:
                self.open_time = self._open_time_base
            if self._close_time_base is not None:
                self.close_time = self._close_time_base
            self._open_time_base = None
            self._close_time_base = None
            self.next_time = None
            self._debug_random("Restored/cleared for loop mode entry")
        self._log_state_change()

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self._open_time_base = None
        self._close_time_base = None
        self.next_time = None
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
        self._log_state_change()