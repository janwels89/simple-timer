import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import io
from fastapi import HTTPException

from PIL import Image

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
controller = None  # Will be set externally

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class ModeChange(BaseModel):
    direction: int

@app.get("/")
def root():
    logger.debug("Serving / (index.html)")
    return FileResponse("static/index.html")

@app.get("/display.png")
def get_display_png():
    logger.debug("Serving /display.png")
    buf = io.BytesIO()
    img = controller.display.fullimage
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

@app.get("/status")
def get_status():
    logger.debug("Serving /status")
    status = {
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
    logger.debug(f"Status: {status}")
    return status

@app.post("/pause_resume")
def pause_resume():
    logger.debug("POST /pause_resume")
    controller._toggle_pause_resume()
    logger.debug(f"Timer enabled: {controller.timer.enabled}")
    return {"enabled": controller.timer.enabled}

@app.post("/reset")
def reset():
    logger.debug("POST /reset")
    controller._reset_and_reload()
    logger.debug("Timer reset")
    return {"status": "reset"}

@app.post("/full_reset")
def full_reset():
    logger.debug("POST /full_reset")
    controller._full_reset()
    logger.debug("Full reset performed")
    return {"status": "full_reset"}

@app.post("/mode")
def change_mode(change: ModeChange):
    logger.debug(f"POST /mode with direction: {change.direction}")
    controller._cycle_timer_mode(change.direction)
    logger.debug(f"New mode: {controller.timer.mode}")
    return {"mode": controller.timer.mode}

@app.post("/key")
async def key_action(request: Request):
    data = await request.json()
    key_num = data.get("key")
    key_map = {1: "KEY1", 2: "KEY2", 3: "KEY3"}
    key_name = key_map.get(key_num)
    logger.debug(f"POST /key with key_num: {key_num} (key_name: {key_name})")
    if key_name and hasattr(controller, "handle_key"):
        controller.handle_key(key_name)
        logger.debug("Key handled")
        return {"status": "ok"}
    logger.debug("Invalid key")
    raise HTTPException(status_code=400, detail="invalid key")

@app.post("/joystick")
async def joystick_action(request: Request):
    data = await request.json()
    direction = data.get("direction")
    logger.debug(f"POST /joystick with direction: {direction}")
    if direction and hasattr(controller, "handle_joystick"):
        controller.handle_joystick(direction)
        logger.debug("Joystick handled")
        return {"status": "ok"}
    logger.debug("Invalid direction")
    raise HTTPException(status_code=400, detail="invalid direction")
