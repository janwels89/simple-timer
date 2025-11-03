#include "input/InputController.hpp"
#include "utils/Logger.hpp"

namespace SimpleTimer {
namespace Input {

ButtonInput::ButtonInput() {
    gpio_ = Device::createGPIODriver();
    
    gpio_->setup(KEY1_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(KEY2_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(KEY3_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    
    Utils::Logger::info("ButtonInput initialized");
}

bool ButtonInput::isPressed(const std::string& keyName) {
    int pin = 0;
    if (keyName == "KEY1") pin = KEY1_PIN;
    else if (keyName == "KEY2") pin = KEY2_PIN;
    else if (keyName == "KEY3") pin = KEY3_PIN;
    else return false;
    
    return gpio_->read(pin) == Device::PinState::LOW;
}

void ButtonInput::cleanup() {
    gpio_->cleanup();
}

JoystickInput::JoystickInput() {
    gpio_ = Device::createGPIODriver();
    
    gpio_->setup(UP_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(DOWN_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(LEFT_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(RIGHT_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    gpio_->setup(PRESS_PIN, Device::PinMode::INPUT, Device::PullMode::UP);
    
    Utils::Logger::info("JoystickInput initialized");
}

bool JoystickInput::isActive(const std::string& direction) {
    int pin = 0;
    if (direction == "up") pin = UP_PIN;
    else if (direction == "down") pin = DOWN_PIN;
    else if (direction == "left") pin = LEFT_PIN;
    else if (direction == "right") pin = RIGHT_PIN;
    else if (direction == "press") pin = PRESS_PIN;
    else return false;
    
    return gpio_->read(pin) == Device::PinState::LOW;
}

void JoystickInput::cleanup() {
    gpio_->cleanup();
}

} // namespace Input
} // namespace SimpleTimer
