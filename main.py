import logging
import time
from app.utils import is_x64, is_debug, run_with_thinkerer

if is_debug():
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

MAX_RESTARTS = 3            # Number of restarts before giving up
RESTART_BACKOFF = 2         # Seconds to sleep before restart

def main_logic(sh1106=None):
    from app.controller import AppController
    debug = is_debug()
    app = AppController(debug=debug, display_hardware=sh1106)
    app.run()

def main():
    restarts = 0
    while restarts < MAX_RESTARTS:
        try:
            if is_x64():
                run_with_thinkerer(main_logic, app_name="App")
            else:
                main_logic()
            # If main_logic exits cleanly, break loop
            break
        except Exception as e:
            logging.error("Fatal error in main loop: %s", e, exc_info=True)
            restarts += 1
            if restarts < MAX_RESTARTS:
                logging.warning("Restarting timer (attempt %d/%d)...", restarts, MAX_RESTARTS)
                time.sleep(RESTART_BACKOFF)
            else:
                logging.critical("Max restarts reached. Exiting for service manager to restart the process.")
                break

if __name__ == '__main__':
    main()