#pragma once

#include "device/GPIO.hpp"
#include <memory>

namespace SimpleTimer {
namespace Input {

class ButtonInput {
public:
    ButtonInput();
    ~ButtonInput() = default;

    bool isPressed(const std::string& keyName);
    void cleanup();

private:
    static constexpr int KEY1_PIN = 21;
    static constexpr int KEY2_PIN = 20;
    static constexpr int KEY3_PIN = 16;
    
    std::shared_ptr<Device::IGPIODriver> gpio_;
};

class JoystickInput {
public:
    JoystickInput();
    ~JoystickInput() = default;

    bool isActive(const std::string& direction);
    void cleanup();

private:
    static constexpr int UP_PIN = 19;
    static constexpr int DOWN_PIN = 6;
    static constexpr int LEFT_PIN = 5;
    static constexpr int RIGHT_PIN = 26;
    static constexpr int PRESS_PIN = 13;
    
    std::shared_ptr<Device::IGPIODriver> gpio_;
};

} // namespace Input
} // namespace SimpleTimer
