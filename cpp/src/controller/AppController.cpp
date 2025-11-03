#include "controller/AppController.hpp"
#include "utils/Logger.hpp"
#include <thread>

namespace SimpleTimer {
namespace Controller {

const std::vector<std::string> AppController::clockSymbols_ = {"|", "/", "-", "\\"};

AppController::AppController()
    : running_(false)
    , selectedTimer_("")
    , key2WasPressed_(false)
    , lastOutputStatus_("OPEN")
    , clockIndex_(0)
    , lastAnimTime_(std::chrono::steady_clock::now())
    , pauseSpin_(false)
{
    timer_ = std::make_unique<Timer::TimerController>();
    display_ = std::make_unique<Display::DisplayController>();
    buttons_ = std::make_unique<Input::ButtonInput>();
    joystick_ = std::make_unique<Input::JoystickInput>();
    output_ = std::make_unique<Output::OutputController>();
    
    timer_->statusA = "";
    timer_->statusB = "";
    timer_->statusC = timer_->mode;
    
    display_->updateValues(*timer_);
    display_->showImage();
    
    Utils::Logger::info("AppController initialized");
}

void AppController::run() {
    running_ = true;
    Utils::Logger::info("AppController running");
    
    while (running_) {
        handleButtons();
        updateTimerAndDisplay();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    buttons_->cleanup();
    joystick_->cleanup();
    output_->cleanup();
}

void AppController::stop() {
    running_ = false;
}

void AppController::updateTimerAndDisplay() {
    auto now = std::chrono::steady_clock::now();
    
    if (timer_->enabled) {
        timer_->update();
        updateOutput();
        
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastAnimTime_).count();
        if (elapsed > 200) {
            clockIndex_ = (clockIndex_ + 1) % clockSymbols_.size();
            lastAnimTime_ = now;
        }
    }
    
    timer_->statusA = clockSymbols_[clockIndex_];
    timer_->statusB = timer_->getStatusB();
    timer_->statusC = (timer_->mode == "loop") ? "" : timer_->mode;
    
    display_->updateValues(*timer_);
    display_->showImage();
}

void AppController::updateOutput() {
    if (timer_->status != lastOutputStatus_) {
        output_->setState(1, timer_->status == "CLOSE");
        lastOutputStatus_ = timer_->status;
    }
}

void AppController::togglePauseResume() {
    timer_->enabled = !timer_->enabled;
    if (timer_->enabled) {
        timer_->resetLastUpdateTime();
        Utils::Logger::info("Timer resumed");
        pauseSpin_ = false;
    } else {
        timer_->status = "OPEN";
        Utils::Logger::info("Timer paused");
        pauseSpin_ = true;
        updateOutput();
    }
}

void AppController::resetTimerCommon() {
    timer_->enabled = false;
    timer_->elapsed = 0;
    timer_->showZero = false;
    pauseSpin_ = true;
}

void AppController::resetAndReload() {
    resetTimerCommon();
    timer_->loadSettings();
    timer_->status = "OPEN";
    updateOutput();
}

void AppController::fullReset() {
    resetTimerCommon();
    timer_->resetSettings();
    timer_->status = "OPEN";
    updateOutput();
}

void AppController::cycleTimerMode(int direction) {
    timer_->cycleMode(direction);
    Utils::Logger::info("Switched to " + timer_->mode + " mode");
}

void AppController::toggleSelection(const std::string& timerType) {
    selectedTimer_ = (selectedTimer_ == timerType) ? "" : timerType;
}

void AppController::exitSelection() {
    selectedTimer_ = "";
}

void AppController::joystickAdjust(int direction) {
    if (selectedTimer_ == "OPEN" || selectedTimer_ == "CLOSE") {
        adjustTimeBase(selectedTimer_, direction);
        timer_->saveSettings();
    } else if (selectedTimer_ == "MODE") {
        timer_->handleModeAdjustment(direction);
    }
}

void AppController::adjustTimeBase(const std::string& timerType, int direction) {
    if (timerType == "OPEN") {
        int newValue = std::max(1, timer_->getOpenTimeBase() + direction);
        timer_->setOpenTimeBase(newValue);
        timer_->randomizeIfNeeded();
        Utils::Logger::info("Adjusted OPEN base time to " + std::to_string(newValue));
    } else if (timerType == "CLOSE") {
        int newValue = std::max(1, timer_->getCloseTimeBase() + direction);
        timer_->setCloseTimeBase(newValue);
        timer_->randomizeIfNeeded();
        Utils::Logger::info("Adjusted CLOSE base time to " + std::to_string(newValue));
    }
}

void AppController::handleButtons() {
    // KEY2: pause/resume or reset/full reset
    if (buttons_->isPressed("KEY2")) {
        if (!key2WasPressed_) {
            key2PressTime_ = std::chrono::steady_clock::now();
            key2WasPressed_ = true;
        }
    } else {
        if (key2WasPressed_) {
            auto duration = std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::steady_clock::now() - key2PressTime_).count();
            
            if (duration >= 5) {
                fullReset();
                Utils::Logger::info("Timer fully reset (KEY2 held ≥5s)");
            } else if (duration >= 2) {
                resetAndReload();
                Utils::Logger::info("Timer reset (KEY2 held ≥2s)");
            } else {
                togglePauseResume();
            }
            key2WasPressed_ = false;
        }
    }
    
    // KEY1/KEY3: select/deselect CLOSE/OPEN
    if (buttons_->isPressed("KEY1")) {
        toggleSelection("CLOSE");
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    if (buttons_->isPressed("KEY3")) {
        toggleSelection("OPEN");
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    // Joystick press: select/deselect MODE
    if (joystick_->isActive("press")) {
        toggleSelection("MODE");
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    // Joystick up/down: adjust selected timer/mode
    if (joystick_->isActive("up")) {
        joystickAdjust(1);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    } else if (joystick_->isActive("down")) {
        joystickAdjust(-1);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    // Joystick left/right: cycle mode
    if (joystick_->isActive("left")) {
        exitSelection();
        cycleTimerMode(-1);
        timer_->statusC = timer_->mode;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    } else if (joystick_->isActive("right")) {
        exitSelection();
        cycleTimerMode(1);
        timer_->statusC = timer_->mode;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

void AppController::handleKey(const std::string& keyName) {
    if (keyName == "KEY2") {
        togglePauseResume();
        exitSelection();
    } else if (keyName == "KEY1") {
        toggleSelection("CLOSE");
    } else if (keyName == "KEY3") {
        toggleSelection("OPEN");
    }
}

void AppController::handleJoystick(const std::string& direction) {
    if (direction == "up") {
        joystickAdjust(1);
    } else if (direction == "down") {
        joystickAdjust(-1);
    } else if (direction == "left") {
        exitSelection();
        cycleTimerMode(-1);
        timer_->statusC = timer_->mode;
    } else if (direction == "right") {
        exitSelection();
        cycleTimerMode(1);
        timer_->statusC = timer_->mode;
    } else if (direction == "press") {
        toggleSelection("MODE");
    }
}

} // namespace Controller
} // namespace SimpleTimer
