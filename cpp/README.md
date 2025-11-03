# Simple Timer - C++ Port

Complete C++ port of the Simple Timer application for Raspberry Pi Zero W2.

## Features

- Full C++ implementation of timer modes (loop, random, add, addsub)
- HTTP REST API compatible with original Python version
- libgpiod-based GPIO control for Raspberry Pi
- SPI display driver for SH1106 OLED
- Desktop mocks for development and testing on x86_64
- Settings persistence via JSON
- PNG generation for web display

## Building

### Prerequisites

#### For Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get install build-essential cmake git libgpiod-dev
```

#### For Desktop (x86_64):
```bash
sudo apt-get update
sudo apt-get install build-essential cmake git
```

### Build on Raspberry Pi

```bash
cd cpp
mkdir build
cd build
cmake .. -DBUILD_DESKTOP_MOCKS=OFF -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

### Build on Desktop with Mocks

```bash
cd cpp
mkdir build
cd build
cmake .. -DBUILD_DESKTOP_MOCKS=ON -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)
```

## Running

### Direct execution:
```bash
cd cpp/build
./simple-timer
```

Add `--debug` flag for verbose logging:
```bash
./simple-timer --debug
```

### Install as systemd service:

```bash
sudo cp simple-timer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable simple-timer
sudo systemctl start simple-timer
```

Check status:
```bash
sudo systemctl status simple-timer
```

View logs:
```bash
sudo journalctl -u simple-timer -f
```

## API Endpoints

The C++ port implements all endpoints from the Python version:

- `GET /` - Serve web interface
- `GET /display.png` - Get current display as PNG
- `GET /status` - Get timer status (JSON)
- `POST /pause_resume` - Toggle timer pause/resume
- `POST /reset` - Reset timer and reload settings
- `POST /full_reset` - Full reset to defaults
- `POST /mode` - Change timer mode (body: `{"direction": 1}`)
- `POST /key` - Simulate key press (body: `{"key": 1}`)
- `POST /joystick` - Simulate joystick (body: `{"direction": "up"}`)

Access the API at `http://<raspberry-pi-ip>:8000`

## Hardware Pin Mapping

### Buttons (BCM numbering):
- KEY1: GPIO21
- KEY2: GPIO20
- KEY3: GPIO16

### Joystick:
- UP: GPIO19
- DOWN: GPIO6
- LEFT: GPIO5
- RIGHT: GPIO26
- PRESS: GPIO13

### Display (SH1106):
- DC: GPIO24
- RST: GPIO25
- SPI: /dev/spidev0.0

### Outputs (Relays):
- Output 1: GPIO4
- Output 2: GPIO17

## GPIO Permissions

For libgpiod access without root, add your user to the gpio group:

```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

Or create a udev rule:
```bash
echo 'SUBSYSTEM=="gpio", KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"' | sudo tee /etc/udev/rules.d/90-gpio.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Testing

Run tests:
```bash
cd cpp/build
ctest --output-on-failure
```

Or run test binary directly:
```bash
./tests/simple-timer-tests
```

## Development Notes

### Desktop Mocks

When `BUILD_DESKTOP_MOCKS=ON`, the application uses mock GPIO and display drivers that simulate hardware behavior without requiring actual Raspberry Pi hardware.

### Code Structure

- `src/device/` - Hardware drivers (GPIO, SH1106)
- `src/timer/` - Timer logic and modes
- `src/display/` - Display rendering and PNG generation
- `src/input/` - Button and joystick handling
- `src/output/` - Relay/output control
- `src/http/` - HTTP API server
- `src/controller/` - Main application controller
- `mocks/` - Desktop mock implementations

### Dependencies

External libraries are fetched automatically by CMake:
- cpp-httplib: HTTP server
- nlohmann/json: JSON parsing
- stb: Image writing

## Troubleshooting

### SPI Permission Error

If you get SPI access errors, ensure SPI is enabled:
```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
sudo reboot
```

And check permissions:
```bash
sudo chmod 666 /dev/spidev0.0
```

Or add user to spi group:
```bash
sudo usermod -a -G spi $USER
```

### libgpiod Not Found

Install libgpiod:
```bash
sudo apt-get install libgpiod-dev
```

## Comparison with Python Version

The C++ port provides:
- Lower memory footprint (~10MB vs ~50MB)
- Faster startup time
- Native binary (no Python runtime required)
- Compatible API and behavior with Python version

All timer modes, display behavior, and API endpoints match the original Python implementation.
