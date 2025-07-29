import time
import sys
from app.timer import TimerController
from app.display import Display

def main(debug=False):
    print(f"[DEBUG] main() starting, debug={debug}")
    display = None
    try:
        display = Display(debug=debug)
        display.hw.Init()
        display.hw.clear()
        time.sleep(0.2)

        from PIL import ImageDraw
        draw = ImageDraw.Draw(display.image)
        draw.rectangle((10, 10, display.width - 10, display.height - 10), outline=0, fill=0)
        display.ShowImage(display.getbuffer(display.image))
        time.sleep(2)
        display.hw.clear()
        print("start timer")

        timer = TimerController()
        timer.status_a = ""
        timer.status_b = ""
        timer.status_c = timer.mode

    timer = TimerController()
        timer.status_a = ""
        timer.status_b = ""
        timer.status_c = timer.mode

        if not debug and hasattr(display, "_is_mock") and display._is_mock():
            print("[INFO] Mock display driver is in use! Set DISPLAY_DRIVER=real or run on ARM hardware for hardware output.")

        display.draw_layout(timer.open_time, timer.close_time, timer.status_a, timer.status_b, timer.status_c)
        display.ShowImage(display.getbuffer(display.image))  # <-- FIXED

        while True:
            timer.update()
            display.update_numbers(timer.open_time, timer.close_time)
            display.ShowImage(display.getbuffer(display.image))  # <-- FIXED
            if debug:
                print(f"[Timer] Status: {timer.status}, Elapsed: {timer.elapsed:.2f}s, Open: {timer.open_time}, Close: {timer.close_time}")
            time.sleep(0.9)
    finally:
        # Always clean up GPIOs if present
        if display is not None and hasattr(display, "hw") and hasattr(display.hw, "RPI"):
            try:
                display.hw.RPI.module_exit()
                print("GPIO cleanup done.")
            except Exception as e:
                print("GPIO cleanup failed:", e)

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    try:
        main(debug=debug)
    except Exception as e:
        print("Exception occurred:", e)
        import traceback
        traceback.print_exc()