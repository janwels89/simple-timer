#pragma once

#include "device/SH1106.hpp"
#include "timer/TimerController.hpp"
#include <vector>
#include <string>
#include <memory>
#include <mutex>

namespace SimpleTimer {
namespace Display {

class DisplayController {
public:
    DisplayController();
    ~DisplayController() = default;

    void updateValues(const Timer::TimerController& timer);
    void showImage();
    void clear();
    
    std::vector<uint8_t> getFramebuffer() const;
    std::vector<uint8_t> generatePNG() const;
    
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }

private:
    void drawLayout(int openNum, int closeNum, 
                   const std::string& statusA, 
                   const std::string& statusB, 
                   const std::string& statusC,
                   int openBase, int closeBase,
                   int openNext, int closeNext,
                   bool flashOpen, bool flashClose);
    
    void drawText(int x, int y, const std::string& text, int size);
    void drawRectangle(int x, int y, int w, int h, bool fill);
    void setPixel(int x, int y, bool value);
    bool getPixel(int x, int y) const;
    
    void createBackground(const std::string& statusA, 
                         const std::string& statusB, 
                         const std::string& statusC);

    int width_;
    int height_;
    std::vector<uint8_t> framebuffer_;
    std::vector<uint8_t> background_;
    std::shared_ptr<Device::IDisplayDriver> driver_;
    mutable std::mutex mutex_;
};

} // namespace Display
} // namespace SimpleTimer
