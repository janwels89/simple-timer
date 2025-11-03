#include "output/OutputController.hpp"
#include "utils/Logger.hpp"

namespace SimpleTimer {
namespace Output {

OutputController::OutputController() {
    gpio_ = Device::createGPIODriver();
    
    gpio_->setup(OUTPUT1_PIN, Device::PinMode::OUTPUT);
    gpio_->setup(OUTPUT2_PIN, Device::PinMode::OUTPUT);
    
    // Set initial state (both OFF)
    gpio_->write(OUTPUT1_PIN, Device::PinState::HIGH);
    gpio_->write(OUTPUT2_PIN, Device::PinState::HIGH);
    
    Utils::Logger::info("OutputController initialized");
}

void OutputController::setState(int outputNumber, bool state) {
    int pin = (outputNumber == 1) ? OUTPUT1_PIN : OUTPUT2_PIN;
    
    // Active LOW logic: relay activates when pin is LOW
    gpio_->write(pin, state ? Device::PinState::LOW : Device::PinState::HIGH);
    
    Utils::Logger::debug("Output " + std::to_string(outputNumber) + 
                        " set to " + (state ? "ON" : "OFF"));
}

bool OutputController::getState(int outputNumber) {
    int pin = (outputNumber == 1) ? OUTPUT1_PIN : OUTPUT2_PIN;
    return gpio_->read(pin) == Device::PinState::LOW;
}

void OutputController::cleanup() {
    gpio_->cleanup();
}

} // namespace Output
} // namespace SimpleTimer
