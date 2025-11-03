#pragma once

#include <cstdint>
#include <vector>
#include <memory>

namespace SimpleTimer {
namespace Device {

class IDisplayDriver {
public:
    virtual ~IDisplayDriver() = default;
    
    virtual int getWidth() const = 0;
    virtual int getHeight() const = 0;
    
    virtual void init() = 0;
    virtual void reset() = 0;
    virtual void clear() = 0;
    virtual void showImage(const std::vector<uint8_t>& buffer) = 0;
};

#ifdef BUILD_DESKTOP_MOCKS
class MockSH1106Driver;
std::shared_ptr<IDisplayDriver> createDisplayDriver();
#else
class SH1106Driver;
std::shared_ptr<IDisplayDriver> createDisplayDriver();
#endif

} // namespace Device
} // namespace SimpleTimer
