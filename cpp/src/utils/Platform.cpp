#include "utils/Platform.hpp"
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

namespace SimpleTimer {
namespace Utils {

bool Platform::isX64() {
#if defined(__x86_64__) || defined(__amd64__)
    return true;
#else
    return false;
#endif
}

bool Platform::isARM() {
#if defined(__arm__) || defined(__aarch64__)
    return true;
#else
    return false;
#endif
}

std::string Platform::getIPAddress(const std::string& interface) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        return "No IP";
    }

    struct ifreq ifr;
    std::memset(&ifr, 0, sizeof(ifr));
    std::strncpy(ifr.ifr_name, interface.c_str(), IFNAMSIZ - 1);

    if (ioctl(fd, SIOCGIFADDR, &ifr) < 0) {
        close(fd);
        return "No IP";
    }

    close(fd);
    
    struct sockaddr_in* addr = (struct sockaddr_in*)&ifr.ifr_addr;
    return std::string(inet_ntoa(addr->sin_addr));
}

} // namespace Utils
} // namespace SimpleTimer
