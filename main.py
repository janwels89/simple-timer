#!/usr/bin/env python3

from app.timer import TimerController
import time

def main():
    timer = TimerController()

    while True:
        timer.update()
        print(f"[Timer] Mode: {timer.mode}, Elapsed: {timer.elapsed:.2f}s")
        time.sleep(0.1)  # adjust for responsiveness vs CPU usage

if __name__ == "__main__":
    main()
