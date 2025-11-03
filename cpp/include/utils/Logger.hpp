#pragma once

#include <iostream>
#include <sstream>
#include <string>
#include <ctime>
#include <iomanip>

namespace SimpleTimer {
namespace Utils {

enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

class Logger {
public:
    static void setLevel(LogLevel level) { globalLevel = level; }
    
    static void debug(const std::string& msg) { log(LogLevel::DEBUG, msg); }
    static void info(const std::string& msg) { log(LogLevel::INFO, msg); }
    static void warning(const std::string& msg) { log(LogLevel::WARNING, msg); }
    static void error(const std::string& msg) { log(LogLevel::ERROR, msg); }

private:
    static LogLevel globalLevel;
    
    static void log(LogLevel level, const std::string& msg) {
        if (level < globalLevel) return;
        
        auto now = std::time(nullptr);
        auto tm = *std::localtime(&now);
        
        std::ostringstream oss;
        oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S") << " [";
        
        switch (level) {
            case LogLevel::DEBUG: oss << "DEBUG"; break;
            case LogLevel::INFO: oss << "INFO"; break;
            case LogLevel::WARNING: oss << "WARNING"; break;
            case LogLevel::ERROR: oss << "ERROR"; break;
        }
        
        oss << "] " << msg << std::endl;
        std::cout << oss.str();
    }
};

} // namespace Utils
} // namespace SimpleTimer
