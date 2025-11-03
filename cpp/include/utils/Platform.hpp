#pragma once

#include <string>

namespace SimpleTimer {
namespace Utils {

class Platform {
public:
    static bool isX64();
    static bool isARM();
    static std::string getIPAddress(const std::string& interface = "wlan0");
};

} // namespace Utils
} // namespace SimpleTimer
