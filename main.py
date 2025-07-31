import logging
from app.utils import is_x64, is_debug, run_with_thinkerer

if is_debug():
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def main_logic(sh1106=None):
    from app.controller import AppController
    debug = is_debug()
    app = AppController(debug=debug, display_hardware=sh1106)
    app.run()

if __name__ == '__main__':
    if is_x64():
        run_with_thinkerer(main_logic, app_name="App")
    else:
        main_logic()