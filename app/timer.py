import time
import os
import json
import logging
from app.timer_modes import LoopModeHandler, RandomModeHandler

SETTINGS_FILE = "settings.json"
logger = logging.getLogger(__name__)

class TimerController:
    DEFAULT_OPEN_TIME = 5
    DEFAULT_CLOSE_TIME = 5

    MODE_HANDLERS = {
        "loop": LoopModeHandler,
        "random": RandomModeHandler,
        # Add future modes here!
    }

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
        self._open_time_base = self.open_time
        self._close_time_base = self.close_time
        self.next_time = None

        self.set_mode(self.mode)
        self.load_settings()
        logger.debug(
            f"TimerController initialized: open={self.open_time}, close={self.close_time}, status={self.status}, mode={self.mode}")

    def set_mode(self, mode):
        self.mode = mode
        handler_cls = self.MODE_HANDLERS.get(mode)
        if not handler_cls:
            raise ValueError(f"Unknown mode: {mode}")
        self.mode_handler = handler_cls(self)
        self.mode_handler.initialize()

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
        logger.debug(
            f"[RANDOM] {msg} | open={self.open_time}, close={self.close_time}, next_time={self.next_time}, base_open={self._open_time_base}, base_close={self._close_time_base}")

    def update(self):
        if not self.enabled:
            return

        now = time.monotonic()
        delta = now - self.last_update_time
        self.last_update_time = now

        time_left = delta
        while time_left > 0:
            if self.show_zero:
                self._debug_random(
                    f"Transition ({self.status}→{'CLOSE' if self.status == 'OPEN' else 'OPEN'}) - BEFORE")
                self.show_zero = False
                self.elapsed = 0
                self.mode_handler.transition()
                self._debug_random(f"Transition ({self.status}) - AFTER")
                self._log_state_change()
                break

            remaining = self.mode_handler.current_remaining_time()
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
        prev_open = self._open_time_base
        prev_close = self._close_time_base
        self.mode_handler.adjust_time(delta)
        self.save_settings()
        if prev_open != self._open_time_base or prev_close != self._close_time_base:
            self._log_state_change()

    def save_settings(self):
        data = {
            "open_time": int(self._open_time_base),
            "close_time": int(self._close_time_base)
        }
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

        self._open_time_base = self.open_time
        self._close_time_base = self.close_time
        self.mode_handler.initialize()
        if loaded:
            self._log_state_change()

    def randomize_if_needed(self):
        self.mode_handler.randomize_if_needed()
        self._log_state_change()

    def reset_settings(self):
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
        self.open_time = self.DEFAULT_OPEN_TIME
        self.close_time = self.DEFAULT_CLOSE_TIME
        self._open_time_base = self.open_time
        self._close_time_base = self.close_time
        self.mode_handler.initialize()
        self.save_settings()
        logger.info("Timer settings reset to defaults.")
        self._log_state_change()

    @property
    def open_time_base(self):
        return self._open_time_base

    @property
    def close_time_base(self):
        return self._close_time_base