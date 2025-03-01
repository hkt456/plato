# main.py
import threading
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from tracker import ActiveTabTracker, tracking_loop
app = FastAPI()
tracker_instance = None
tracking_thread = None
stop_event = None

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def get_status():
    """
    Return whether the tracking thread is currently running.
    """
    global tracking_thread
    if tracking_thread and tracking_thread.is_alive():
        return {"running": True}
    else:
        return {"running": False}


@app.post("/start_tracking")
def start_tracking():
    global tracker_instance, tracking_thread, stop_event
    if tracking_thread and tracking_thread.is_alive():
        return {"status": "already tracking"}

    tracker_instance = ActiveTabTracker()
    stop_event = threading.Event()

    tracking_thread = threading.Thread(
        target=tracking_loop,
        args=(tracker_instance, stop_event),
        daemon=True
    )
    tracking_thread.start()
    return {"status": "tracking started"}

@app.post("/stop_tracking")
def stop_tracking():
    global tracking_thread, stop_event
    if not tracking_thread or not tracking_thread.is_alive():
        return {"status": "no active tracking"}

    stop_event.set()
    tracking_thread.join()
    tracking_thread = None
    return {"status": "tracking stopped"}

@app.post("/visibility")
async def receive_visibility(request: Request):
    """
    Endpoint called by the Chrome extension's content script whenever a tab becomes
    visible or hidden.
    Example payload:
      {
        "tabUrl": "https://example.com",
        "state": "visible" or "hidden",
        "timestamp": 1683311223456
      }
    """
    global tracker_instance
    if not tracker_instance:
        return {"error": "Tracker not running. Start tracking first."}

    data = await request.json()
    tab_url = data.get("tabUrl", "unknown_tab")
    state = data.get("state", "hidden")

    if state == "visible":
        tracker_instance.on_tab_visible(tab_url, tab_url)
    else:
        tracker_instance.on_tab_hidden(tab_url)

    return {"status": "ok"}

@app.get("/usage")
def get_usage():
    """
    Return the current in-memory usage data.
    """
    global tracker_instance
    if not tracker_instance:
        return {"error": "No tracker instance. Start tracking first."}
    return tracker_instance.total_times

@app.get("/usage_json")
def get_usage_json():
    """
    Return the persisted usage data from tab_usage.json, if it exists.
    """
    try:
        with open("tab_usage.json", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": "Could not read tab_usage.json", "details": str(e)}

