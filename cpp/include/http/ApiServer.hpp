#pragma once

#include "controller/AppController.hpp"
#include <memory>
#include <thread>
#include <atomic>

namespace SimpleTimer {
namespace HTTP {

class ApiServer {
public:
    ApiServer(Controller::AppController* controller);
    ~ApiServer();

    void start(int port = 8000);
    void stop();

private:
    Controller::AppController* controller_;
    std::unique_ptr<std::thread> serverThread_;
    std::atomic<bool> running_;
};

} // namespace HTTP
} // namespace SimpleTimer
