import platform
import sys

def is_x64():
    arch = platform.machine().lower()
    return 'x86_64' in arch or 'amd64' in arch

def is_debug():
    return '--debug' in sys.argv

def run_with_thinkerer(run_app, app_name="App"):
    """
    Runs the given callable in a background thread and launches the Thinkerer mock display GUI on x64.
    - run_app: function to start your app or test logic, accepting one argument: sh1106
    - app_name: str, label for print messages
    """
    import threading
    from features.steps.mocks.mock_sh1106 import SH1106
    sh1106 = SH1106()
    thinkerer = sh1106.thinkerer  # This will create Thinkerer window

    # Launch app logic in background, passing the *same* sh1106 to the test logic
    app_thread = threading.Thread(target=lambda: run_app(sh1106), daemon=True)
    app_thread.start()

    # Start Tkinter mainloop in main thread
    if thinkerer:
        print(f"Launching Thinkerer mock display window for x64 ({app_name}).")
        thinkerer.root.mainloop()
    else:
        print(f"Thinkerer not available, running {app_name.lower()} logic only.")
        app_thread.join()