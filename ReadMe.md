# Simple Timer

## Overview

Simple Timer is a multi-mode timer application designed for Raspberry Pi Zero W2 with support for hardware display, buttons, joystick, and relay outputs. Available in both Python and C++ implementations.

## Implementations

### C++ Port (Recommended for Production)
See [cpp/README.md](cpp/README.md) for the complete C++ implementation with:
- Native performance and lower memory usage
- libgpiod-based GPIO control
- Desktop mocks for development
- Full API compatibility with Python version
- systemd service integration

### Python Version (Reference)
Original Python implementation in `python-backup/` directory.

## Features

- **Multi-Mode Timer**: Supports loop, random, add, and add/subtract timer modes.
- **HTTP REST API**: Web interface and API endpoints (port 8000).
- **Persistent Settings**: Timer settings saved to `settings.json`.
- **Hardware Integration**: SH1106 OLED display, buttons, joystick, relay outputs.
- **Extensible**: Modular design with separate mode handlers and controller logic.

## Project Structure

### C++ Implementation
```
cpp/
├── src/
│   ├── device/         # GPIO and SH1106 drivers
│   ├── timer/          # Timer controller and modes
│   ├── display/        # Display rendering and PNG generation
│   ├── input/          # Button and joystick handling
│   ├── output/         # Relay control
│   ├── http/           # HTTP API server
│   ├── controller/     # Main application controller
│   ├── utils/          # Platform utilities and logging
│   └── main.cpp        # Application entry point
├── include/            # Header files
├── mocks/              # Desktop mock implementations
├── tests/              # Unit tests
├── CMakeLists.txt      # Build configuration
├── README.md           # C++ port documentation
└── install.sh          # Installation script

### Python Reference Implementation (in python-backup/)
```
python-backup/
├── app/
│   ├── api.py             # FastAPI/uvicorn API interface
│   ├── controller.py      # AppController for hardware/display integration
│   ├── display.py         # Display controller
│   ├── input.py           # InputController for hardware buttons
│   ├── output.py          # OutputController for hardware outputs
│   ├── timer.py           # TimerController managing timer logic
│   ├── timer_modes.py     # Loop, Random, Add, AddSub handlers
│   └── utils.py           # Platform utilities
├── device/                # Hardware integration
│   └── SH1106.py          # SH1106 display driver
├── main.py                # Entry point
└── requirements.txt

## Quick Start

### C++ Version (Recommended)

#### On Raspberry Pi:
```bash
cd cpp
./install.sh
```

This will build and install the C++ version as a systemd service.

#### On Desktop (for development):
```bash
cd cpp
mkdir build && cd build
cmake .. -DBUILD_DESKTOP_MOCKS=ON
make
./simple-timer --debug
```

Access the web interface at [http://localhost:8000](http://localhost:8000)

For detailed C++ documentation, see [cpp/README.md](cpp/README.md)

### Python Version (Reference)

See `python-backup/` directory for the original Python implementation.

## Timer Modes

- **loop**: Alternates between open/close at fixed intervals.
- **random**: Open/close times are randomized within configured ranges.
- **add**: Each cycle adds to closed time
- **addsub**: Adds and subtracts increments from open to close time

You can cycle and adjust modes via the API or hardware interface (buttons/joystick).

## API Endpoints

- `GET /` - Web interface
- `GET /display.png` - Current display as PNG
- `GET /status` - Timer status (JSON)
- `POST /pause_resume` - Toggle pause/resume
- `POST /reset` - Reset and reload settings
- `POST /full_reset` - Full reset to defaults
- `POST /mode` - Change mode (body: `{"direction": 1}`)
- `POST /key` - Simulate key press (body: `{"key": 1|2|3}`)
- `POST /joystick` - Simulate joystick (body: `{"direction": "up|down|left|right|press"}`)

## Settings Persistence

Timer settings (open/close times, increments) are auto-saved to `settings.json` and reloaded on startup.

---

**Author:** [janwels89](https://github.com/janwels89)