#!/usr/bin/env python3

from app.timer import TimerController
from app.display import Display



def main():
    timer = TimerController()
    display = Display()

    while True:
        timer.update()
        display.show_timer(timer)  # Update the display with timer info
        print(f"[Timer] Mode: {timer.mode}, Elapsed: {timer.elapsed:.2f}s")
        time.sleep(0.1)  # adjust for responsiveness vs CPU usage

if __name__ == "__main__":
    main()