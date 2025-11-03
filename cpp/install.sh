#!/bin/bash
# Install script for Simple Timer C++ on Raspberry Pi

set -e

echo "Installing Simple Timer C++ Service..."

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "Warning: This does not appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential cmake git libgpiod-dev

# Build the project
echo "Building project..."
cd "$(dirname "$0")"
mkdir -p build
cd build
cmake .. -DBUILD_DESKTOP_MOCKS=OFF -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Install systemd service
echo "Installing systemd service..."
sudo cp ../simple-timer.service /etc/systemd/system/
sudo sed -i "s|/home/pi/simple-timer|$(realpath ../..)|g" /etc/systemd/system/simple-timer.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable simple-timer
sudo systemctl start simple-timer

echo "Installation complete!"
echo ""
echo "Service status:"
sudo systemctl status simple-timer --no-pager
echo ""
echo "Useful commands:"
echo "  View logs:    sudo journalctl -u simple-timer -f"
echo "  Stop service: sudo systemctl stop simple-timer"
echo "  Restart:      sudo systemctl restart simple-timer"
echo "  Disable:      sudo systemctl disable simple-timer"
