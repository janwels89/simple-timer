#include "device/SH1106.hpp"
#include "utils/Logger.hpp"
#include <vector>
#include <fstream>

namespace SimpleTimer {
namespace Device {

class MockSH1106Driver : public IDisplayDriver {
public:
    MockSH1106Driver() : width_(128), height_(64) {
        buffer_.resize((width_ * height_) / 8, 0xFF);
        Utils::Logger::info("Mock SH1106 driver initialized");
    }

    int getWidth() const override { return width_; }
    int getHeight() const override { return height_; }

    void init() override {
        Utils::Logger::debug("Mock SH1106: init()");
    }

    void reset() override {
        Utils::Logger::debug("Mock SH1106: reset()");
    }

    void clear() override {
        buffer_.assign((width_ * height_) / 8, 0xFF);
        Utils::Logger::debug("Mock SH1106: clear()");
    }

    void showImage(const std::vector<uint8_t>& buffer) override {
        buffer_ = buffer;
        Utils::Logger::debug("Mock SH1106: showImage() with buffer size " + 
                           std::to_string(buffer.size()));
    }

    const std::vector<uint8_t>& getBuffer() const {
        return buffer_;
    }

private:
    int width_;
    int height_;
    std::vector<uint8_t> buffer_;
};

std::shared_ptr<IDisplayDriver> createDisplayDriver() {
    return std::make_shared<MockSH1106Driver>();
}

} // namespace Device
} // namespace SimpleTimer
