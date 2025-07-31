import sys
import platform

def is_x64():
    arch = platform.machine().lower()
    return 'x86_64' in arch or 'amd64' in arch

if is_x64():
    # ---- X64: Start Thinkerer GUI in main thread, app logic in background ----
    import threading
    from features.steps.mocks.mock_sh1106 import SH1106, Thinkerer  # import these here to avoid Tkinter import on ARM
    from app.controller import AppController
    import time

    def run_app():
        debug = '--debug' in sys.argv
        app = AppController(debug=debug)
        app.run()

    # Create display mock to ensure GUI is up
    sh1106 = SH1106()
    thinkerer = sh1106.thinkerer  # This will create Thinkerer window

    # Launch app logic in background
    app_thread = threading.Thread(target=run_app, daemon=True)
    app_thread.start()

    # Start Tkinter mainloop in main thread
    if thinkerer:
        print("Launching Thinkerer mock display window for x64.")
        thinkerer.root.mainloop()
    else:
        print("Thinkerer not available, running app only.")
        app_thread.join()
else:
    # ---- ARM (Raspberry Pi): Run as normal, no GUI ----
    from app.controller import AppController

    def main():
        debug = '--debug' in sys.argv
        app = AppController(debug=debug)
        app.run()
    if __name__ == '__main__':
        main()