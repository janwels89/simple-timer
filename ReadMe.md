# Simple Timer

## Features

- **Multi-Mode Timer**: Supports loop, random, add, and add/subtract timer modes.
- **HTTP & HTTPS REST API**: Runs API servers in parallel (port 8000 for HTTP, 8443 for HTTPS).
- **Persistent Settings**: Timer settings are saved and loaded from `settings.json`.
- **Threaded Operation**: Runs API endpoints and timer logic concurrently.
- **Extensible**: Modular design with separate mode handlers and controller logic.

## Project Structure

```
simple-timer/
├── app/
│   ├── api.py             # FastAPI/uvicorn API interface
│   ├── controller.py      # AppController for hardware/display integration
│   ├── display.py         #  display controller
│   ├── input.py           # InputController for hardware buttons
│   ├── output.py          # OutputController for hardware outputs
│   ├── timer.py           # TimerController managing timer logic
│   ├── timer_modes.py     # Loop, Random, Add, AddSub handlers
│   └── utils.py           # is_x64, is_debug, run_with_thinkerer utilities
├── device/                # hardware integration (e.g., SH1106 display, GPIO)  
│   ├── sh1106.py          # SH1106 display driver
│   └── gpio.py            # GPIO control for hardware buttons
├── main.py                # Entry point orchestrating controllers and APIs
├── requirements.txt
├── features/             # behave tests for different timer modes
├── fonts/                 # Font files for display rendering
├── static/                # Static HTML files for Webinterface
├── tests/                # Unit tests for the application

```

## Quickstart

### 1. Clone and Install

```bash
git clone https://github.com/janwels89/simple-timer.git
cd simple-timer
pip install -r requirements.txt
```

### 2. Run the Timer Service

Start the main service (which launches both HTTP and HTTPS APIs):

```bash
python main.py
```

- HTTP API available at: [http://localhost:8000](http://localhost:8000)
- HTTPS API available at: [https://localhost:8443](https://localhost:8443) (requires `key.pem` and `cert.pem` in the root directory)

### 3. API Endpoints

See the API documentation (typically FastAPI/OpenAPI) at `/docs` once the server is running.

### 4. Modes

- **loop**: Alternates between open/close at fixed intervals.
- **random**: Open/close times are randomized within configured ranges.
- **add**: Each cycle adds to closed time
- **addsub**: Adds and subtracts increments from open to close time

You can cycle and adjust modes via the API or the hardware interface (if connected).

### 5. Settings Persistence

Timer settings (open/close times, increments) are auto-saved to `settings.json` and reloaded on startup.

---

**Author:** [janwels89](https://github.com/janwels89)