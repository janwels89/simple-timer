from app.utils import is_x64, is_debug, run_with_thinkerer

def main_logic(sh1106):
    from app.controller import AppController
    # If your AppController allows, pass the hardware:
    app = AppController(debug=is_debug(), display_hardware=sh1106)
    app.run()

if is_x64():
    run_with_thinkerer(main_logic, app_name="App")
else:
    from app.controller import AppController

    def main():
        app = AppController(debug=is_debug())
        app.run()
    if __name__ == '__main__':
        main()