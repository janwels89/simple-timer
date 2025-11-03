#include "controller/AppController.hpp"
#include "http/ApiServer.hpp"
#include "utils/Logger.hpp"
#include <thread>
#include <csignal>
#include <atomic>

std::atomic<bool> keepRunning(true);

void signalHandler(int) {
    keepRunning = false;
}

int main(int argc, char** argv) {
    // Check for debug flag
    for (int i = 1; i < argc; i++) {
        if (std::string(argv[i]) == "--debug") {
            SimpleTimer::Utils::Logger::setLevel(SimpleTimer::Utils::LogLevel::DEBUG);
        }
    }
    
    SimpleTimer::Utils::Logger::info("Simple Timer C++ starting...");
    
    // Setup signal handler
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);
    
    try {
        // Create app controller
        auto appController = std::make_unique<SimpleTimer::Controller::AppController>();
        
        // Create and start HTTP server
        auto apiServer = std::make_unique<SimpleTimer::HTTP::ApiServer>(appController.get());
        apiServer->start(8000);
        
        // Run app controller in main thread
        std::thread appThread([&appController]() {
            appController->run();
        });
        
        // Wait for signal
        while (keepRunning) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        
        SimpleTimer::Utils::Logger::info("Shutting down...");
        
        appController->stop();
        apiServer->stop();
        
        if (appThread.joinable()) {
            appThread.join();
        }
        
        SimpleTimer::Utils::Logger::info("Shutdown complete");
        
    } catch (const std::exception& e) {
        SimpleTimer::Utils::Logger::error("Fatal error: " + std::string(e.what()));
        return 1;
    }
    
    return 0;
}
