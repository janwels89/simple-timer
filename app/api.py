# app/api.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
controller = None  # Will be set externally

class ModeChange(BaseModel):
    direction: int

@app.get("/status")
def get_status():
    return {
        "enabled": controller.timer.enabled,
        "status": controller.timer.status,
        "mode": controller.timer.mode,
        "elapsed": int(controller.timer.elapsed),
        "open_time": controller.timer.open_time,
        "close_time": controller.timer.close_time,
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