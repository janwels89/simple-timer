#include "utils/Logger.hpp"
#include "utils/Platform.hpp"
#include <iostream>
#include <cassert>

int main() {
    using namespace SimpleTimer::Utils;
    
    Logger::info("Running basic tests...");
    
    // Test platform detection
    bool isX64 = Platform::isX64();
    bool isARM = Platform::isARM();
    
    Logger::info("Platform: x64=" + std::string(isX64 ? "true" : "false") + 
                ", ARM=" + std::string(isARM ? "true" : "false"));
    
    // Test IP address retrieval (may fail if interface doesn't exist)
    std::string ip = Platform::getIPAddress("lo");
    Logger::info("IP address (lo): " + ip);
    
    Logger::info("All basic tests passed!");
    
    return 0;
}
