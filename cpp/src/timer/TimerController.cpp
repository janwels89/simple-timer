#include "timer/TimerController.hpp"
#include "timer/TimerModes.hpp"
#include "utils/Logger.hpp"
#include <fstream>
#include <nlohmann/json.hpp>
#include <algorithm>

using json = nlohmann::json;

namespace SimpleTimer {
namespace Timer {

TimerController::TimerController()
    : openTime(DEFAULT_OPEN_TIME)
    , closeTime(DEFAULT_CLOSE_TIME)
    , status("OPEN")
    , mode("loop")
    , enabled(false)
    , elapsed(0.0)
    , showZero(false)
    , zeroStatus("")
    , nextTime(0)
    , addIncrement(1)
    , statusA("")
    , statusB("")
    , statusC("")
    , openTimeBase_(DEFAULT_OPEN_TIME)
    , closeTimeBase_(DEFAULT_CLOSE_TIME)
    , lastUpdateTime_(std::chrono::steady_clock::now())
{
    setMode("loop");
    loadSettings();
    Utils::Logger::info("TimerController initialized");
}

void TimerController::setMode(const std::string& newMode) {
    mode = newMode;
    
    if (newMode == "loop") {
        modeHandler_ = std::make_unique<LoopModeHandler>(this);
    } else if (newMode == "random") {
        modeHandler_ = std::make_unique<RandomModeHandler>(this);
    } else if (newMode == "add") {
        modeHandler_ = std::make_unique<AddModeHandler>(this);
    } else if (newMode == "addsub") {
        modeHandler_ = std::make_unique<AddSubModeHandler>(this);
    } else {
        Utils::Logger::error("Unknown mode: " + newMode);
        modeHandler_ = std::make_unique<LoopModeHandler>(this);
        mode = "loop";
    }
    
    modeHandler_->initialize();
}

void TimerController::cycleMode(int direction) {
    std::vector<std::string> modes = {"loop", "random", "add", "addsub"};
    auto it = std::find(modes.begin(), modes.end(), mode);
    int idx = (it != modes.end()) ? std::distance(modes.begin(), it) : 0;
    
    idx = (idx + direction + modes.size()) % modes.size();
    setMode(modes[idx]);
}

void TimerController::handleModeAdjustment(int direction) {
    if (modeHandler_) {
        modeHandler_->adjust(direction);
    }
}

std::string TimerController::getStatusB() const {
    return modeHandler_ ? modeHandler_->getStatusB() : "";
}

void TimerController::update() {
    if (!enabled) {
        return;
    }

    auto now = std::chrono::steady_clock::now();
    double delta = std::chrono::duration<double>(now - lastUpdateTime_).count();
    lastUpdateTime_ = now;

    double timeLeft = delta;
    while (timeLeft > 0) {
        if (showZero) {
            showZero = false;
            zeroStatus = "";
            elapsed = 0;
            modeHandler_->transition();
            break;
        }

        double remaining = modeHandler_->currentRemainingTime();
        if (remaining > 0) {
            if (timeLeft >= remaining) {
                elapsed += remaining;
                timeLeft -= remaining;
                showZero = true;
                zeroStatus = status;
                break;
            } else {
                elapsed += timeLeft;
                timeLeft = 0;
            }
        } else {
            showZero = true;
            zeroStatus = status;
            break;
        }
    }
}

void TimerController::adjustTime(int delta) {
    if (modeHandler_) {
        modeHandler_->adjustTime(delta);
        saveSettings();
    }
}

void TimerController::saveSettings() {
    json j;
    j["open_time"] = openTimeBase_;
    j["close_time"] = closeTimeBase_;
    j["add_increment"] = addIncrement;

    std::ofstream file("settings.json");
    if (file.is_open()) {
        file << j.dump(4);
        file.close();
        Utils::Logger::info("Settings saved");
    } else {
        Utils::Logger::error("Failed to save settings");
    }
}

void TimerController::loadSettings() {
    std::ifstream file("settings.json");
    if (!file.is_open()) {
        Utils::Logger::info("No settings file found, using defaults");
        return;
    }

    try {
        json j;
        file >> j;
        file.close();

        openTime = j.value("open_time", DEFAULT_OPEN_TIME);
        closeTime = j.value("close_time", DEFAULT_CLOSE_TIME);
        addIncrement = j.value("add_increment", 1);
        
        openTimeBase_ = openTime;
        closeTimeBase_ = closeTime;
        
        if (modeHandler_) {
            modeHandler_->initialize();
        }
        
        Utils::Logger::info("Settings loaded");
    } catch (const std::exception& e) {
        Utils::Logger::error("Failed to load settings: " + std::string(e.what()));
    }
}

void TimerController::randomizeIfNeeded() {
    if (modeHandler_) {
        modeHandler_->randomizeIfNeeded();
    }
}

void TimerController::resetSettings() {
    std::remove("settings.json");
    
    openTime = DEFAULT_OPEN_TIME;
    closeTime = DEFAULT_CLOSE_TIME;
    addIncrement = 1;
    openTimeBase_ = openTime;
    closeTimeBase_ = closeTime;
    
    if (modeHandler_) {
        modeHandler_->initialize();
    }
    
    saveSettings();
    status = "OPEN";
    Utils::Logger::info("Settings reset to defaults");
}

} // namespace Timer
} // namespace SimpleTimer
