#include "device/GPIO.hpp"
#include "utils/Logger.hpp"
#include <gpiod.h>
#include <map>
#include <stdexcept>

namespace SimpleTimer {
namespace Device {

class LibGpiodDriver : public IGPIODriver {
public:
    LibGpiodDriver() : chip_(nullptr) {
        chip_ = gpiod_chip_open_by_name("gpiochip0");
        if (!chip_) {
            throw std::runtime_error("Failed to open GPIO chip");
        }
        Utils::Logger::info("LibGpiod driver initialized");
    }

    ~LibGpiodDriver() {
        cleanup();
    }

    void setup(int pin, PinMode mode, PullMode pull) override {
        struct gpiod_line* line = gpiod_chip_get_line(chip_, pin);
        if (!line) {
            throw std::runtime_error("Failed to get GPIO line " + std::to_string(pin));
        }

        int flags = 0;
        if (pull == PullMode::UP) {
            flags = GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP;
        } else if (pull == PullMode::DOWN) {
            flags = GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_DOWN;
        }

        int ret;
        if (mode == PinMode::INPUT) {
            ret = gpiod_line_request_input_flags(line, "simple-timer", flags);
        } else {
            ret = gpiod_line_request_output(line, "simple-timer", 0);
        }

        if (ret < 0) {
            throw std::runtime_error("Failed to request GPIO line " + std::to_string(pin));
        }

        lines_[pin] = line;
    }

    PinState read(int pin) override {
        auto it = lines_.find(pin);
        if (it == lines_.end()) {
            throw std::runtime_error("Pin " + std::to_string(pin) + " not setup");
        }

        int value = gpiod_line_get_value(it->second);
        return (value == 1) ? PinState::HIGH : PinState::LOW;
    }

    void write(int pin, PinState state) override {
        auto it = lines_.find(pin);
        if (it == lines_.end()) {
            throw std::runtime_error("Pin " + std::to_string(pin) + " not setup");
        }

        int value = (state == PinState::HIGH) ? 1 : 0;
        gpiod_line_set_value(it->second, value);
    }

    void cleanup() override {
        for (auto& pair : lines_) {
            if (pair.second) {
                gpiod_line_release(pair.second);
            }
        }
        lines_.clear();

        if (chip_) {
            gpiod_chip_close(chip_);
            chip_ = nullptr;
        }
        Utils::Logger::info("LibGpiod driver cleanup complete");
    }

private:
    struct gpiod_chip* chip_;
    std::map<int, struct gpiod_line*> lines_;
};

std::shared_ptr<IGPIODriver> createGPIODriver() {
    return std::make_shared<LibGpiodDriver>();
}

} // namespace Device
} // namespace SimpleTimer
