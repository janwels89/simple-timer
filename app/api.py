# api.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import io
from PIL import Image

app = FastAPI()
controller = None  # Will be set externally

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class ModeChange(BaseModel):
    direction: int

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/display.png")
def get_display_png():
    buf = io.BytesIO()
    # Apply the same rotation/flip as in Display.getbuffer
    img = controller.display.image
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

@app.get("/status")
def get_status():
    return {
        "mode": controller.timer.mode,
        "enabled": controller.timer.enabled,
        "status": controller.timer.status,
        "add_increment": controller.timer.add_increment,
        "show_zero": controller.timer.show_zero,
        "zero_status": controller.timer.zero_status,
        "next_time": controller.timer.next_time,
        "open_time": controller.timer.open_time,
        "close_time": controller.timer.close_time,
        "elapsed": int(controller.timer.elapsed),
     }

@app.post("/pause_resume")
def pause_resume():
    controller._toggle_pause_resume()
    return {"enabled": controller.timer.enabled}

@app.post("/reset")
def reset():
    controller._reset_and_reload()
    return {"status": "reset"}

@app.post("/full_reset")
def full_reset():
    controller._full_reset()
    return {"status": "full_reset"}

@app.post("/mode")
def change_mode(change: ModeChange):
    controller._cycle_timer_mode(change.direction)
    return {"mode": controller.timer.mode}

@app.post("/key")
async def key_action(request: Request):
    data = await request.json()
    key_num = data.get("key")
    key_map = {1: "KEY1", 2: "KEY2", 3: "KEY3"}
    key_name = key_map.get(key_num)
    if key_name and hasattr(controller, "handle_key"):
        controller.handle_key(key_name)
        return {"status": "ok"}
    return {"status": "invalid key"}, 400

@app.post("/joystick")
async def joystick_action(request: Request):
    data = await request.json()
    direction = data.get("direction")
    if direction and hasattr(controller, "handle_joystick"):
        controller.handle_joystick(direction)
        return {"status": "ok"}
    return {"status": "invalid direction"}, 400