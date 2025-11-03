#pragma once

#include "device/GPIO.hpp"
#include <memory>

namespace SimpleTimer {
namespace Output {

class OutputController {
public:
    OutputController();
    ~OutputController() = default;

    void setState(int outputNumber, bool state);
    bool getState(int outputNumber);
    void cleanup();

private:
    static constexpr int OUTPUT1_PIN = 4;
    static constexpr int OUTPUT2_PIN = 17;
    
    std::shared_ptr<Device::IGPIODriver> gpio_;
};

} // namespace Output
} // namespace SimpleTimer
