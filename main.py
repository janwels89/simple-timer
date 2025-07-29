import time
from app.timer import TimerController
from app.display import Display

def main():
    display = Display()
    timer = TimerController()
    timer.status_a = ""
    timer.status_b = ""
    timer.status_c = timer.mode

    # Draw the static layout ONCE at the beginning
    display.draw_layout(timer.open_time, timer.close_time, timer.status_a, timer.status_b, timer.status_c)
    display.hw.ShowImage(display.hw.getbuffer(display.image))

    while True:
        timer.update()
        display.update_numbers(timer.open_time, timer.close_time)
        display.hw.ShowImage(display.hw.getbuffer(display.image))
        print(f"[Timer] Status: {timer.status}, Elapsed: {timer.elapsed:.2f}s")
        time.sleep(0.1)

if __name__ == "__main__":
    main()