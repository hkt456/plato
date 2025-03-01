import threading
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from tracker import ActiveTabTracker, tracking_loop  # Your tracking module
from session_analysis import SessionAnalysis         # Import the analysis class

app = FastAPI()
tracker_instance = None
tracking_thread = None
stop_event = None

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

@app.post("/analysis_report")
async def generate_analysis_report(request: Request):
    """
    Generate an analysis report using the latest tracker data (from /usage_json),
    a hardcoded pose_data, and a session goal provided by the user in the JSON payload.

    Expects a JSON payload like:
    {
      "session_goal": "..."
    }
    """
    # Parse the request JSON to retrieve session goal
    data = await request.json()
    session_goal = data.get("session_goal", "")

    if session_goal == "":
        return {"error": "Missing required field: session_goal."}

    # Retrieve the latest tracker data from tab_usage.json
    usage_response = get_usage_json()
    if "error" in usage_response:
        return {"error": "Could not retrieve tracker data from usage_json."}

    tracker_data = usage_response  # The usage_json endpoint returns a dictionary if successful

    # Hardcode the pose_data
    pose_data = {
        "Humpedback": 3.0,
        "Wrong distance": 4.0,
        "Shoulder deviation": 5.0
    }

    # Create the analysis report
    analysis = SessionAnalysis(tracker_data, pose_data, session_goal)
    report = analysis.get_analysis_report()

    if report:
        # Preprocess the report for Markdown rendering
        markdown_report = (
            report
            .replace("\\r", "")
            .replace("\\n\\n", "\n\n")
            .replace("\\n", "  \n")
        )
        return {"analysis_report": markdown_report}
    else:
        return {"error": "Failed to generate analysis report."}

@app.get("/analysis_report_test")
def analysis_report_test():
    """
    Test endpoint to generate an analysis report using hardcoded JSON samples.
    """
    # Hardcoded sample JSON from the tracker
    tracker_data = {
        "https://chatgpt.com/c/67c2317b-594c-800b-b5d8-014c3e4fbc0b": {
            "time": 3.0005178451538086,
            "title": "https://chatgpt.com/c/67c2317b-594c-800b-b5d8-014c3e4fbc0b"
        },
        "http://127.0.0.1:8000/usage": {
            "time": 8.001509189605713,
            "title": "http://127.0.0.1:8000/usage"
        },
        "http://127.0.0.1:8000/usage_json": {
            "time": 2.000476598739624,
            "title": "http://127.0.0.1:8000/usage_json"
        }
    }

    # Hardcoded sample JSON from pose detection
    pose_data = {
        "Humpedback": 3.0,
        "Wrong distance": 4.0,
        "Shoulder deviation": 5.0
    }
    
    # Hardcoded session goal
    session_goal = "Complete coding tasks efficiently"
    
    analysis = SessionAnalysis(tracker_data, pose_data, session_goal)
    report = analysis.get_analysis_report()
    
    if report:
        # Preprocess for Markdown rendering
        markdown_report = (
            report
            .replace("\\r", "")
            .replace("\\n\\n", "\n\n")
            .replace("\\n", "  \n")
        )
        return {"analysis_report": markdown_report}
    else:
        return {"error": "Failed to generate analysis report."}

