#pragma once

#include <string>
#include <memory>

namespace SimpleTimer {
namespace Timer {

class TimerController; // Forward declaration

class IModeHandler {
public:
    virtual ~IModeHandler() = default;
    
    virtual void initialize() = 0;
    virtual void transition() = 0;
    virtual void setNextTime() = 0;
    virtual void adjustTime(int delta) = 0;
    virtual void adjust(int direction) = 0;
    virtual double currentRemainingTime() const = 0;
    virtual void randomizeIfNeeded() = 0;
    virtual int getIncrement() const = 0;
    virtual std::string getStatusB() const = 0;
    
protected:
    TimerController* timer_;
};

class LoopModeHandler : public IModeHandler {
public:
    explicit LoopModeHandler(TimerController* timer) { timer_ = timer; }
    
    void initialize() override;
    void transition() override;
    void setNextTime() override;
    void adjustTime(int delta) override;
    void adjust(int direction) override {} // No adjustment for loop mode
    double currentRemainingTime() const override;
    void randomizeIfNeeded() override {}
    int getIncrement() const override { return 1; }
    std::string getStatusB() const override;
};

class RandomModeHandler : public IModeHandler {
public:
    explicit RandomModeHandler(TimerController* timer) { timer_ = timer; }
    
    void initialize() override;
    void transition() override;
    void setNextTime() override;
    void adjustTime(int delta) override;
    void adjust(int direction) override { }
    double currentRemainingTime() const override;
    void randomizeIfNeeded() override;
    int getIncrement() const override { return 1; }
    std::string getStatusB() const override { return ""; }
    
private:
    int randomPeriod(const std::string& period) const;
};

class AddModeHandler : public IModeHandler {
public:
    explicit AddModeHandler(TimerController* timer) : accumulated_(0), firstCycle_(true), resetNext_(false) { 
        timer_ = timer; 
    }
    
    void initialize() override;
    void transition() override;
    void setNextTime() override;
    void adjustTime(int delta) override;
    void adjust(int direction) override;
    double currentRemainingTime() const override;
    void randomizeIfNeeded() override;
    int getIncrement() const override;
    std::string getStatusB() const override;
    
private:
    void updateTimes();
    int accumulated_;
    bool firstCycle_;
    bool resetNext_;
};

class AddSubModeHandler : public IModeHandler {
public:
    explicit AddSubModeHandler(TimerController* timer) : accumulated_(0) { 
        timer_ = timer; 
    }
    
    void initialize() override;
    void transition() override;
    void setNextTime() override;
    void adjustTime(int delta) override;
    void adjust(int direction) override;
    double currentRemainingTime() const override;
    void randomizeIfNeeded() override;
    int getIncrement() const override;
    std::string getStatusB() const override;
    
private:
    void resetToBase();
    void updateTimes();
    int accumulated_;
};

} // namespace Timer
} // namespace SimpleTimer
