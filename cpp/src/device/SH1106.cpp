#include "device/SH1106.hpp"
#include "device/GPIO.hpp"
#include "utils/Logger.hpp"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <cstring>
#include <thread>
#include <chrono>

namespace SimpleTimer {
namespace Device {

class SH1106Driver : public IDisplayDriver {
public:
    SH1106Driver() : spi_fd_(-1), width_(128), height_(64) {
        gpio_ = createGPIODriver();
        
        // Setup DC and RST pins
        gpio_->setup(DC_PIN, PinMode::OUTPUT);
        gpio_->setup(RST_PIN, PinMode::OUTPUT);
        
        // Open SPI device
        spi_fd_ = open("/dev/spidev0.0", O_RDWR);
        if (spi_fd_ < 0) {
            throw std::runtime_error("Failed to open SPI device");
        }
        
        // Configure SPI
        uint8_t mode = SPI_MODE_3;
        uint8_t bits = 8;
        uint32_t speed = 1000000; // 1 MHz
        
        ioctl(spi_fd_, SPI_IOC_WR_MODE, &mode);
        ioctl(spi_fd_, SPI_IOC_WR_BITS_PER_WORD, &bits);
        ioctl(spi_fd_, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
        
        Utils::Logger::info("SH1106 SPI driver initialized");
    }

    ~SH1106Driver() {
        if (spi_fd_ >= 0) {
            close(spi_fd_);
        }
    }

    int getWidth() const override { return width_; }
    int getHeight() const override { return height_; }

    void init() override {
        reset();
        
        // Initialization sequence for SH1106
        command(0xAE); // Display off
        command(0x02); // Set low column address
        command(0x10); // Set high column address
        command(0x40); // Set start line address
        command(0x81); // Set contrast control
        command(0xA0); // Set segment remap
        command(0xC0); // Set COM output scan direction
        command(0xA6); // Set normal display
        command(0xA8); // Set multiplex ratio
        command(0x3F); // 1/64 duty
        command(0xD3); // Set display offset
        command(0x00); // No offset
        command(0xD5); // Set display clock divide ratio
        command(0x80); // Set divide ratio
        command(0xD9); // Set pre-charge period
        command(0xF1); // Set pre-charge
        command(0xDA); // Set COM pins hardware configuration
        command(0x12);
        command(0xDB); // Set VCOMH
        command(0x40); // Set VCOM deselect level
        command(0x20); // Set page addressing mode
        command(0x02);
        command(0xA4); // Disable entire display on
        command(0xA6); // Disable inverse display
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        command(0xAF); // Display on
        
        Utils::Logger::info("SH1106 initialized");
    }

    void reset() override {
        gpio_->write(RST_PIN, PinState::HIGH);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        gpio_->write(RST_PIN, PinState::LOW);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        gpio_->write(RST_PIN, PinState::HIGH);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    void clear() override {
        std::vector<uint8_t> buffer((width_ * height_) / 8, 0xFF);
        showImage(buffer);
    }

    void showImage(const std::vector<uint8_t>& buffer) override {
        for (int page = 0; page < 8; page++) {
            command(0xB0 + page);  // Set page address
            command(0x02);         // Set low column address
            command(0x10);         // Set high column address
            
            // Write data
            gpio_->write(DC_PIN, PinState::HIGH);
            
            for (int i = 0; i < width_; i++) {
                uint8_t inverted = ~buffer[i + width_ * page];
                write(spi_fd_, &inverted, 1);
            }
        }
    }

private:
    void command(uint8_t cmd) {
        gpio_->write(DC_PIN, PinState::LOW);
        write(spi_fd_, &cmd, 1);
    }

    static constexpr int DC_PIN = 24;
    static constexpr int RST_PIN = 25;
    
    int spi_fd_;
    int width_;
    int height_;
    std::shared_ptr<IGPIODriver> gpio_;
};

std::shared_ptr<IDisplayDriver> createDisplayDriver() {
    return std::make_shared<SH1106Driver>();
}

} // namespace Device
} // namespace SimpleTimer
