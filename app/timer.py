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
        self.next_open_time = None
        self.next_close_time = None
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
            "next_open_time": self.next_open_time,
            "next_close_time": self.next_close_time,
        }
        if state != self._last_state:
            logger.info(
                "Timer state changed: open_time=%s, close_time=%s, status=%s, enabled=%s, elapsed=%.3f, show_zero=%s, next_open=%s, next_close=%s",
                self.open_time, self.close_time, self.status, self.enabled, self.elapsed, self.show_zero, self.next_open_time, self.next_close_time
            )
            self._last_state = state.copy()

    def update(self):
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
                # Switch state
                if self.status == "OPEN":
                    self.status = "CLOSE"
                    if self.mode == "random":
                        # ONLY assign close_time from buffer, then randomize NEXT close buffer
                        self.close_time = self.next_close_time
                        self.next_close_time = self._random_period("CLOSE")
                else:
                    self.status = "OPEN"
                    if self.mode == "random":
                        # ONLY assign open_time from buffer, then randomize NEXT open buffer
                        self.open_time = self.next_open_time
                        self.next_open_time = self._random_period("OPEN")
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
            elif self.status == "CLOSE":
                self._close_time_base = max(1, self._close_time_base + delta)
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

    def _change_time(self, attr, delta):
        prev = getattr(self, attr)
        new_value = max(1, prev + delta)
        setattr(self, attr, new_value)
        self.save_settings()
        if prev != new_value:
            self._log_state_change()

    def increase_open_time(self):
        self._change_time('open_time', +1)

    def decrease_open_time(self):
        self._change_time('open_time', -1)

    def increase_close_time(self):
        self._change_time('close_time', +1)

    def decrease_close_time(self):
        self._change_time('close_time', -1)

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
            self.next_open_time = self._random_period("OPEN")
            self.next_close_time = self._random_period("CLOSE")

        if loaded:
            self._log_state_change()

    def _random_period(self, period):
        if period == "OPEN":
            base = self._open_time_base or self.DEFAULT_OPEN_TIME
        else:
            base = self._close_time_base or self.DEFAULT_CLOSE_TIME
        # Minimum of 1, random uniform between 1 and base*2 (classic: base +/- 100%)
        return max(1, int(round(random.uniform(base * 0.5, base))))

    def randomize_if_needed(self):
        """Randomize all values ONCE, only when entering random mode."""
        if self.mode == "random":
            if self._open_time_base is None:
                self._open_time_base = self.open_time
            if self._close_time_base is None:
                self._close_time_base = self.close_time

            self.open_time = self._random_period("OPEN")
            self.next_open_time = self._random_period("OPEN")
            self.close_time = self._random_period("CLOSE")
            self.next_close_time = self._random_period("CLOSE")
            logger.debug("Randomized all values once when entering random mode.")
        else:
            if self._open_time_base is not None:
                self.open_time = self._open_time_base
                self.close_time = self._close_time_base
                self._open_time_base = None
                self._close_time_base = None
                self.next_open_time = None
                self.next_close_time = None
                logger.debug("Restored base times.")
        self._log_state_change()

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self._open_time_base = None
        self._close_time_base = None
        self.next_open_time = None
        self.next_close_time = None
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
        self._log_state_change()