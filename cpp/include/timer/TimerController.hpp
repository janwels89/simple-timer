#pragma once

#include "timer/TimerModes.hpp"
#include <string>
#include <memory>
#include <chrono>

namespace SimpleTimer {
namespace Timer {

class TimerController {
public:
    TimerController();
    ~TimerController() = default;

    // State
    int openTime;
    int closeTime;
    std::string status;
    std::string mode;
    bool enabled;
    double elapsed;
    bool showZero;
    std::string zeroStatus;
    int nextTime;
    int addIncrement;
    
    // Status fields for display
    std::string statusA;
    std::string statusB;
    std::string statusC;

    // Methods
    void update();
    void setMode(const std::string& newMode);
    void cycleMode(int direction);
    void handleModeAdjustment(int direction);
    std::string getStatusB() const;
    void adjustTime(int delta);
    void saveSettings();
    void loadSettings();
    void randomizeIfNeeded();
    void resetSettings();
    
    // Accessors
    int getOpenTimeBase() const { return openTimeBase_; }
    int getCloseTimeBase() const { return closeTimeBase_; }
    void setOpenTimeBase(int value) { openTimeBase_ = value; }
    void setCloseTimeBase(int value) { closeTimeBase_; }
    void resetLastUpdateTime() { lastUpdateTime_ = std::chrono::steady_clock::now(); }

private:
    static constexpr int DEFAULT_OPEN_TIME = 5;
    static constexpr int DEFAULT_CLOSE_TIME = 5;
    
    int openTimeBase_;
    int closeTimeBase_;
    std::chrono::steady_clock::time_point lastUpdateTime_;
    std::unique_ptr<IModeHandler> modeHandler_;
    
    friend class LoopModeHandler;
    friend class RandomModeHandler;
    friend class AddModeHandler;
    friend class AddSubModeHandler;
};

} // namespace Timer
} // namespace SimpleTimer
