#include "timer/TimerModes.hpp"
#include "timer/TimerController.hpp"
#include "utils/Platform.hpp"
#include <random>
#include <algorithm>

namespace SimpleTimer {
namespace Timer {

// LoopModeHandler implementation
void LoopModeHandler::initialize() {
    timer_->openTime = timer_->openTimeBase_;
    timer_->closeTime = timer_->closeTimeBase_;
    setNextTime();
}

void LoopModeHandler::transition() {
    if (timer_->status == "OPEN") {
        timer_->status = "CLOSE";
        timer_->closeTime = timer_->closeTimeBase_;
        timer_->nextTime = timer_->openTimeBase_;
    } else {
        timer_->status = "OPEN";
        timer_->openTime = timer_->openTimeBase_;
        timer_->nextTime = timer_->closeTimeBase_;
    }
}

void LoopModeHandler::setNextTime() {
    if (timer_->status == "OPEN") {
        timer_->nextTime = timer_->closeTimeBase_;
    } else {
        timer_->nextTime = timer_->openTimeBase_;
    }
}

void LoopModeHandler::adjustTime(int delta) {
    if (timer_->status == "OPEN") {
        timer_->openTimeBase_ = std::max(1, timer_->openTimeBase_ + delta);
    } else {
        timer_->closeTimeBase_ = std::max(1, timer_->closeTimeBase_ + delta);
    }
    initialize();
}

double LoopModeHandler::currentRemainingTime() const {
    return (timer_->status == "OPEN" ? timer_->openTime : timer_->closeTime) - timer_->elapsed;
}

std::string LoopModeHandler::getStatusB() const {
    return Utils::Platform::getIPAddress();
}

// RandomModeHandler implementation
void RandomModeHandler::initialize() {
    if (timer_->status == "OPEN") {
        timer_->openTime = randomPeriod("OPEN");
        timer_->nextTime = randomPeriod("CLOSE");
    } else {
        timer_->closeTime = randomPeriod("CLOSE");
        timer_->nextTime = randomPeriod("OPEN");
    }
}

int RandomModeHandler::randomPeriod(const std::string& period) const {
    int base = (period == "OPEN") ? timer_->openTimeBase_ : timer_->closeTimeBase_;
    
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, std::max(1, base));
    
    return dis(gen);
}

void RandomModeHandler::transition() {
    if (timer_->status == "OPEN") {
        timer_->status = "CLOSE";
        timer_->closeTime = timer_->nextTime;
        timer_->nextTime = randomPeriod("OPEN");
    } else {
        timer_->status = "OPEN";
        timer_->openTime = timer_->nextTime;
        timer_->nextTime = randomPeriod("CLOSE");
    }
}

void RandomModeHandler::setNextTime() {
    if (timer_->status == "OPEN") {
        timer_->nextTime = randomPeriod("CLOSE");
    } else {
        timer_->nextTime = randomPeriod("OPEN");
    }
}

void RandomModeHandler::adjustTime(int delta) {
    if (timer_->status == "OPEN") {
        timer_->openTimeBase_ = std::max(1, timer_->openTimeBase_ + delta);
        timer_->nextTime = randomPeriod("CLOSE");
    } else {
        timer_->closeTimeBase_ = std::max(1, timer_->closeTimeBase_ + delta);
        timer_->nextTime = randomPeriod("OPEN");
    }
}

void RandomModeHandler::randomizeIfNeeded() {
    setNextTime();
}

double RandomModeHandler::currentRemainingTime() const {
    return (timer_->status == "OPEN" ? timer_->openTime : timer_->closeTime) - timer_->elapsed;
}

// AddModeHandler implementation
void AddModeHandler::initialize() {
    accumulated_ = 0;
    firstCycle_ = true;
    resetNext_ = false;
    updateTimes();
    setNextTime();
}

void AddModeHandler::updateTimes() {
    timer_->openTime = timer_->openTimeBase_;
    timer_->closeTime = timer_->closeTimeBase_ + accumulated_;
}

void AddModeHandler::transition() {
    if (resetNext_) {
        accumulated_ = 0;
        resetNext_ = false;
        timer_->status = "OPEN";
        updateTimes();
        setNextTime();
        return;
    }

    if (timer_->status == "OPEN") {
        if (timer_->openTime <= 0) {
            resetNext_ = true;
        }
        timer_->status = "CLOSE";
        updateTimes();
        setNextTime();
    } else {
        if (!resetNext_) {
            accumulated_ += timer_->addIncrement;
            timer_->status = "OPEN";
            updateTimes();
            setNextTime();
        } else {
            transition();
        }
    }
}

void AddModeHandler::setNextTime() {
    if (resetNext_ && timer_->status == "CLOSE") {
        timer_->nextTime = timer_->openTimeBase_;
    } else if (timer_->status == "OPEN") {
        int nextAccum = accumulated_ + (firstCycle_ ? 0 : timer_->addIncrement);
        timer_->nextTime = timer_->closeTimeBase_ + nextAccum;
    } else {
        timer_->nextTime = timer_->openTimeBase_;
    }
}

void AddModeHandler::adjustTime(int delta) {
    if (timer_->status == "OPEN") {
        timer_->openTimeBase_ = std::max(1, timer_->openTimeBase_ + delta);
    } else {
        timer_->closeTimeBase_ = std::max(1, timer_->closeTimeBase_ + delta);
    }
    setNextTime();
}

void AddModeHandler::adjust(int direction) {
    timer_->addIncrement = std::max(1, timer_->addIncrement + direction);
    setNextTime();
}

double AddModeHandler::currentRemainingTime() const {
    return (timer_->status == "OPEN" ? timer_->openTime : timer_->closeTime) - timer_->elapsed;
}

void AddModeHandler::randomizeIfNeeded() {
    initialize();
}

int AddModeHandler::getIncrement() const {
    return timer_->addIncrement;
}

std::string AddModeHandler::getStatusB() const {
    return "inc: " + std::to_string(timer_->addIncrement);
}

// AddSubModeHandler implementation
void AddSubModeHandler::initialize() {
    accumulated_ = 0;
    resetToBase();
    timer_->status = "OPEN";
    setNextTime();
}

void AddSubModeHandler::resetToBase() {
    timer_->openTime = timer_->openTimeBase_;
    timer_->closeTime = timer_->closeTimeBase_;
}

void AddSubModeHandler::updateTimes() {
    timer_->openTime = timer_->openTimeBase_ - accumulated_ * timer_->addIncrement;
    timer_->closeTime = timer_->closeTimeBase_ + accumulated_ * timer_->addIncrement;
}

void AddSubModeHandler::transition() {
    if (timer_->status == "OPEN") {
        int nextOpen = timer_->openTimeBase_ - (accumulated_ + 1) * timer_->addIncrement;
        if (nextOpen < 1) {
            accumulated_ = 0;
            resetToBase();
            timer_->status = "OPEN";
            setNextTime();
            return;
        }
        timer_->status = "CLOSE";
        updateTimes();
        setNextTime();
    } else {
        accumulated_ += 1;
        timer_->status = "OPEN";
        updateTimes();
        setNextTime();
    }
}

void AddSubModeHandler::setNextTime() {
    if (timer_->status == "OPEN") {
        timer_->nextTime = timer_->closeTimeBase_ + accumulated_ * timer_->addIncrement;
    } else {
        timer_->nextTime = timer_->openTimeBase_ - (accumulated_ + 1) * timer_->addIncrement;
    }
}

void AddSubModeHandler::adjustTime(int delta) {
    if (timer_->status == "OPEN") {
        timer_->openTimeBase_ = std::max(1, timer_->openTimeBase_ + delta);
    } else {
        timer_->closeTimeBase_ = std::max(1, timer_->closeTimeBase_ + delta);
    }
    setNextTime();
}

void AddSubModeHandler::adjust(int direction) {
    timer_->addIncrement = std::max(1, timer_->addIncrement + direction);
    setNextTime();
}

double AddSubModeHandler::currentRemainingTime() const {
    if (timer_->status == "OPEN") {
        return std::max(0.0, timer_->openTime - timer_->elapsed);
    } else {
        return timer_->closeTime - timer_->elapsed;
    }
}

void AddSubModeHandler::randomizeIfNeeded() {
    initialize();
}

int AddSubModeHandler::getIncrement() const {
    return timer_->addIncrement;
}

std::string AddSubModeHandler::getStatusB() const {
    return "inc: " + std::to_string(timer_->addIncrement);
}

} // namespace Timer
} // namespace SimpleTimer
