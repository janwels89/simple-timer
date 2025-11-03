#pragma once

#include "timer/TimerController.hpp"
#include "display/DisplayController.hpp"
#include "input/InputController.hpp"
#include "output/OutputController.hpp"
#include <memory>
#include <atomic>
#include <chrono>

namespace SimpleTimer {
namespace Controller {

class AppController {
public:
    AppController();
    ~AppController() = default;

    void run();
    void stop();
    
    // API methods
    void togglePauseResume();
    void resetAndReload();
    void fullReset();
    void cycleTimerMode(int direction);
    void handleKey(const std::string& keyName);
    void handleJoystick(const std::string& direction);
    
    // Accessors
    Timer::TimerController& getTimer() { return *timer_; }
    Display::DisplayController& getDisplay() { return *display_; }

private:
    void handleButtons();
    void updateTimerAndDisplay();
    void updateOutput();
    void toggleSelection(const std::string& timerType);
    void exitSelection();
    void joystickAdjust(int direction);
    void adjustTimeBase(const std::string& timerType, int direction);
    void resetTimerCommon();
    
    std::unique_ptr<Timer::TimerController> timer_;
    std::unique_ptr<Display::DisplayController> display_;
    std::unique_ptr<Input::ButtonInput> buttons_;
    std::unique_ptr<Input::JoystickInput> joystick_;
    std::unique_ptr<Output::OutputController> output_;
    
    std::atomic<bool> running_;
    std::string selectedTimer_;
    bool key2WasPressed_;
    std::chrono::steady_clock::time_point key2PressTime_;
    
    std::string lastOutputStatus_;
    int clockIndex_;
    std::chrono::steady_clock::time_point lastAnimTime_;
    bool pauseSpin_;
    
    static const std::vector<std::string> clockSymbols_;
};

} // namespace Controller
} // namespace SimpleTimer
