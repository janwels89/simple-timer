#include "display/DisplayController.hpp"
#include "utils/Logger.hpp"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include <cstring>
#include <algorithm>

namespace SimpleTimer {
namespace Display {

DisplayController::DisplayController() : width_(128), height_(64) {
    driver_ = Device::createDisplayDriver();
    framebuffer_.resize((width_ * height_) / 8, 0xFF);
    background_.resize((width_ * height_) / 8, 0xFF);
    
    driver_->init();
    driver_->clear();
    
    Utils::Logger::info("DisplayController initialized");
}

void DisplayController::setPixel(int x, int y, bool value) {
    if (x < 0 || x >= width_ || y < 0 || y >= height_) return;
    
    int byteIndex = x + (y / 8) * width_;
    int bitIndex = y % 8;
    
    if (value) {
        framebuffer_[byteIndex] &= ~(1 << bitIndex);
    } else {
        framebuffer_[byteIndex] |= (1 << bitIndex);
    }
}

bool DisplayController::getPixel(int x, int y) const {
    if (x < 0 || x >= width_ || y < 0 || y >= height_) return false;
    
    int byteIndex = x + (y / 8) * width_;
    int bitIndex = y % 8;
    
    return !(framebuffer_[byteIndex] & (1 << bitIndex));
}

void DisplayController::drawRectangle(int x, int y, int w, int h, bool fill) {
    for (int i = 0; i < w; i++) {
        for (int j = 0; j < h; j++) {
            if (fill || i == 0 || i == w-1 || j == 0 || j == h-1) {
                setPixel(x + i, y + j, true);
            }
        }
    }
}

void DisplayController::drawText(int x, int y, const std::string& text, int size) {
    // Simplified text rendering - just render numbers and basic text
    // In production, use a proper font renderer or freetype
    for (size_t i = 0; i < text.length(); i++) {
        char c = text[i];
        int cx = x + i * (size + 1);
        
        // Simple 5x7 character rendering for digits
        if (c >= '0' && c <= '9') {
            // Draw a simple representation
            for (int dy = 0; dy < 7; dy++) {
                for (int dx = 0; dx < 5; dx++) {
                    setPixel(cx + dx, y + dy, true);
                }
            }
        }
    }
}

void DisplayController::createBackground(const std::string& statusA, 
                                        const std::string& statusB, 
                                        const std::string& statusC) {
    background_.assign((width_ * height_) / 8, 0xFF);
    
    // Draw status bar at top (16 pixels high)
    for (int x = 0; x < width_; x++) {
        for (int y = 0; y < 16; y++) {
            int byteIndex = x + (y / 8) * width_;
            int bitIndex = y % 8;
            background_[byteIndex] &= ~(1 << bitIndex);
        }
    }
}

void DisplayController::drawLayout(int openNum, int closeNum, 
                                  const std::string& statusA, 
                                  const std::string& statusB, 
                                  const std::string& statusC,
                                  int openBase, int closeBase,
                                  int openNext, int closeNext,
                                  bool flashOpen, bool flashClose) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    createBackground(statusA, statusB, statusC);
    framebuffer_ = background_;
    
    // Draw "OPEN" label and number at y=18
    drawText(5, 18, "OPEN", 18);
    drawText(width_ - 40, 20, std::to_string(flashOpen ? 0 : openNum), 18);
    
    // Draw "CLOSE" label and number at y=42
    drawText(5, 42, "CLOSE", 18);
    drawText(width_ - 40, 44, std::to_string(flashClose ? 0 : closeNum), 18);
    
    // Draw status text
    drawText(2, 2, statusA, 10);
    drawText(width_/2 - 10, 2, statusB.substr(0, 8), 10);
    drawText(width_ - 40, 2, statusC, 10);
}

void DisplayController::updateValues(const Timer::TimerController& timer) {
    int openBase = timer.getOpenTimeBase();
    int closeBase = timer.getCloseTimeBase();
    
    bool flashOpen = timer.showZero && timer.zeroStatus == "OPEN";
    bool flashClose = timer.showZero && timer.zeroStatus == "CLOSE";
    
    int openRemaining = flashOpen ? 0 : 
        (timer.status == "OPEN" ? std::max(0, static_cast<int>(timer.openTime - timer.elapsed)) : timer.nextTime);
    
    int closeRemaining = flashClose ? 0 :
        (timer.status == "OPEN" ? timer.nextTime : std::max(0, static_cast<int>(timer.closeTime - timer.elapsed)));
    
    int openNext = (timer.status == "OPEN") ? timer.nextTime : 0;
    int closeNext = (timer.status == "CLOSE") ? timer.nextTime : 0;
    
    drawLayout(openRemaining, closeRemaining,
              timer.statusA, timer.statusB, timer.statusC,
              openBase, closeBase,
              openNext, closeNext,
              flashOpen, flashClose);
}

void DisplayController::showImage() {
    std::lock_guard<std::mutex> lock(mutex_);
    driver_->showImage(framebuffer_);
}

void DisplayController::clear() {
    driver_->clear();
}

std::vector<uint8_t> DisplayController::getFramebuffer() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return framebuffer_;
}

std::vector<uint8_t> DisplayController::generatePNG() const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // Convert framebuffer to RGB image
    std::vector<uint8_t> image(width_ * height_ * 3);
    
    for (int y = 0; y < height_; y++) {
        for (int x = 0; x < width_; x++) {
            bool pixel = getPixel(x, y);
            int idx = (y * width_ + x) * 3;
            uint8_t value = pixel ? 255 : 0;
            image[idx] = value;
            image[idx + 1] = value;
            image[idx + 2] = value;
        }
    }
    
    // Encode as PNG
    int len;
    unsigned char* png = stbi_write_png_to_mem(
        image.data(), width_ * 3, width_, height_, 3, &len);
    
    std::vector<uint8_t> result(png, png + len);
    free(png);
    
    return result;
}

} // namespace Display
} // namespace SimpleTimer
