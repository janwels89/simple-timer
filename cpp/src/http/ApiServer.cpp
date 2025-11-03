#include "http/ApiServer.hpp"
#include "utils/Logger.hpp"
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <fstream>

using json = nlohmann::json;

namespace SimpleTimer {
namespace HTTP {

ApiServer::ApiServer(Controller::AppController* controller)
    : controller_(controller), running_(false) {
}

ApiServer::~ApiServer() {
    stop();
}

void ApiServer::start(int port) {
    running_ = true;
    
    serverThread_ = std::make_unique<std::thread>([this, port]() {
        httplib::Server svr;
        
        // Serve static files
        svr.set_mount_point("/static", "./static");
        
        // GET /
        svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
            std::ifstream file("static/index.html");
            if (file.is_open()) {
                std::string content((std::istreambuf_iterator<char>(file)),
                                   std::istreambuf_iterator<char>());
                res.set_content(content, "text/html");
            } else {
                res.status = 404;
            }
        });
        
        // GET /display.png
        svr.Get("/display.png", [this](const httplib::Request&, httplib::Response& res) {
            try {
                auto png = controller_->getDisplay().generatePNG();
                res.set_content(std::string(png.begin(), png.end()), "image/png");
            } catch (const std::exception& e) {
                Utils::Logger::error("Failed to generate PNG: " + std::string(e.what()));
                res.status = 500;
            }
        });
        
        // GET /status
        svr.Get("/status", [this](const httplib::Request&, httplib::Response& res) {
            auto& timer = controller_->getTimer();
            json j = {
                {"mode", timer.mode},
                {"enabled", timer.enabled},
                {"status", timer.status},
                {"add_increment", timer.addIncrement},
                {"show_zero", timer.showZero},
                {"zero_status", timer.zeroStatus},
                {"next_time", timer.nextTime},
                {"open_time", timer.openTime},
                {"close_time", timer.closeTime},
                {"elapsed", static_cast<int>(timer.elapsed)}
            };
            res.set_content(j.dump(), "application/json");
        });
        
        // POST /pause_resume
        svr.Post("/pause_resume", [this](const httplib::Request&, httplib::Response& res) {
            controller_->togglePauseResume();
            json j = {{"enabled", controller_->getTimer().enabled}};
            res.set_content(j.dump(), "application/json");
        });
        
        // POST /reset
        svr.Post("/reset", [this](const httplib::Request&, httplib::Response& res) {
            controller_->resetAndReload();
            json j = {{"status", "reset"}};
            res.set_content(j.dump(), "application/json");
        });
        
        // POST /full_reset
        svr.Post("/full_reset", [this](const httplib::Request&, httplib::Response& res) {
            controller_->fullReset();
            json j = {{"status", "full_reset"}};
            res.set_content(j.dump(), "application/json");
        });
        
        // POST /mode
        svr.Post("/mode", [this](const httplib::Request& req, httplib::Response& res) {
            try {
                auto j = json::parse(req.body);
                int direction = j.value("direction", 1);
                controller_->cycleTimerMode(direction);
                json resp = {{"mode", controller_->getTimer().mode}};
                res.set_content(resp.dump(), "application/json");
            } catch (const std::exception& e) {
                res.status = 400;
                json err = {{"error", e.what()}};
                res.set_content(err.dump(), "application/json");
            }
        });
        
        // POST /key
        svr.Post("/key", [this](const httplib::Request& req, httplib::Response& res) {
            try {
                auto j = json::parse(req.body);
                int keyNum = j.value("key", 0);
                std::string keyName = (keyNum == 1) ? "KEY1" : 
                                     (keyNum == 2) ? "KEY2" : 
                                     (keyNum == 3) ? "KEY3" : "";
                
                if (!keyName.empty()) {
                    controller_->handleKey(keyName);
                    json resp = {{"status", "ok"}};
                    res.set_content(resp.dump(), "application/json");
                } else {
                    res.status = 400;
                    json err = {{"error", "invalid key"}};
                    res.set_content(err.dump(), "application/json");
                }
            } catch (const std::exception& e) {
                res.status = 400;
                json err = {{"error", e.what()}};
                res.set_content(err.dump(), "application/json");
            }
        });
        
        // POST /joystick
        svr.Post("/joystick", [this](const httplib::Request& req, httplib::Response& res) {
            try {
                auto j = json::parse(req.body);
                std::string direction = j.value("direction", "");
                
                if (!direction.empty()) {
                    controller_->handleJoystick(direction);
                    json resp = {{"status", "ok"}};
                    res.set_content(resp.dump(), "application/json");
                } else {
                    res.status = 400;
                    json err = {{"error", "invalid direction"}};
                    res.set_content(err.dump(), "application/json");
                }
            } catch (const std::exception& e) {
                res.status = 400;
                json err = {{"error", e.what()}};
                res.set_content(err.dump(), "application/json");
            }
        });
        
        Utils::Logger::info("HTTP server starting on port " + std::to_string(port));
        svr.listen("0.0.0.0", port);
    });
}

void ApiServer::stop() {
    running_ = false;
    if (serverThread_ && serverThread_->joinable()) {
        serverThread_->join();
    }
}

} // namespace HTTP
} // namespace SimpleTimer
