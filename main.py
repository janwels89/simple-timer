import logging
import time
import threading
from app.utils import is_x64, is_debug, run_with_thinkerer

if is_debug():
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

MAX_RESTARTS = 3
RESTART_BACKOFF = 2

def start_api_http():
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=False)

def start_api_https():
    import uvicorn
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8443,
        reload=False,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )

def main_logic(sh1106=None):
    from app.controller import AppController
    import app.api
    debug = is_debug()
    app_controller = AppController(debug=debug, display_hardware=sh1106)
    app.api.controller = app_controller  # Set before starting API servers

    # Start both HTTP and HTTPS API servers in background threads
    http_thread = threading.Thread(target=start_api_http, daemon=True)
    https_thread = threading.Thread(target=start_api_https, daemon=True)
    http_thread.start()
    https_thread.start()

    app_controller.run()

def main():
    restarts = 0
    while restarts < MAX_RESTARTS:
        try:
            if is_x64():
                run_with_thinkerer(main_logic, app_name="App")
            else:
                main_logic()
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