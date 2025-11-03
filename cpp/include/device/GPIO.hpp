#pragma once

#include <cstdint>
#include <string>
#include <memory>

namespace SimpleTimer {
namespace Device {

enum class PinMode {
    INPUT,
    OUTPUT
};

enum class PullMode {
    NONE,
    UP,
    DOWN
};

enum class PinState {
    LOW = 0,
    HIGH = 1
};

class IGPIODriver {
public:
    virtual ~IGPIODriver() = default;
    
    virtual void setup(int pin, PinMode mode, PullMode pull = PullMode::NONE) = 0;
    virtual PinState read(int pin) = 0;
    virtual void write(int pin, PinState state) = 0;
    virtual void cleanup() = 0;
};

#ifdef BUILD_DESKTOP_MOCKS
class MockGPIODriver;
std::shared_ptr<IGPIODriver> createGPIODriver();
#else
class LibGpiodDriver;
std::shared_ptr<IGPIODriver> createGPIODriver();
#endif

} // namespace Device
} // namespace SimpleTimer
