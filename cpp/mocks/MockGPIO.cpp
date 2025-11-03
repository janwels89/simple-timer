#include "device/GPIO.hpp"
#include "utils/Logger.hpp"
#include <map>
#include <mutex>

namespace SimpleTimer {
namespace Device {

class MockGPIODriver : public IGPIODriver {
public:
    MockGPIODriver() {
        Utils::Logger::info("Mock GPIO driver initialized");
    }

    void setup(int pin, PinMode mode, PullMode pull) override {
        std::lock_guard<std::mutex> lock(mutex_);
        pins_[pin] = PinConfig{mode, pull, PinState::HIGH};
        Utils::Logger::debug("Mock GPIO: setup(pin=" + std::to_string(pin) + 
                           ", mode=" + (mode == PinMode::INPUT ? "INPUT" : "OUTPUT") + ")");
    }

    PinState read(int pin) override {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = pins_.find(pin);
        if (it == pins_.end()) {
            return PinState::HIGH; // Default for unsetup pins
        }
        return it->second.state;
    }

    void write(int pin, PinState state) override {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = pins_.find(pin);
        if (it != pins_.end()) {
            it->second.state = state;
            Utils::Logger::debug("Mock GPIO: write(pin=" + std::to_string(pin) + 
                               ", state=" + (state == PinState::HIGH ? "HIGH" : "LOW") + ")");
        }
    }

    void cleanup() override {
        std::lock_guard<std::mutex> lock(mutex_);
        pins_.clear();
        Utils::Logger::info("Mock GPIO driver cleanup complete");
    }

    // Mock-specific methods for testing
    void simulatePress(int pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = pins_.find(pin);
        if (it != pins_.end()) {
            it->second.state = PinState::LOW;
        }
    }

    void simulateRelease(int pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = pins_.find(pin);
        if (it != pins_.end()) {
            it->second.state = PinState::HIGH;
        }
    }

private:
    struct PinConfig {
        PinMode mode;
        PullMode pull;
        PinState state;
    };

    std::map<int, PinConfig> pins_;
    std::mutex mutex_;
};

std::shared_ptr<IGPIODriver> createGPIODriver() {
    return std::make_shared<MockGPIODriver>();
}

} // namespace Device
} // namespace SimpleTimer
