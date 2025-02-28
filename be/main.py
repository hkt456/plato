# main.py
import threading
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from tracker import ActiveTabTracker, tracking_loop

app = FastAPI(
    title="Tab Tracking API (WebSocket)",
    description="Tracks time spent on visible Chrome tabs and streams updates via WebSocket.",
    version="1.0.0"
)

# Global tracker instance shared between the background thread and API endpoints.
tracker_instance = ActiveTabTracker()
tracking_thread = None

def startup_event():
    """
    Start the background tracking thread when the FastAPI application starts.
    """
    global tracking_thread, tracker_instance
    tracking_thread = threading.Thread(target=tracking_loop, args=(tracker_instance,))
    tracking_thread.daemon = True  # Ensure the thread exits when the app shuts down.
    tracking_thread.start()
    print("Started background tracking thread.")

def shutdown_event():
    """
    Finalize any visible tabs and write usage data on application shutdown.
    """
    if tracking_thread and tracking_thread.is_alive():
        tracker_instance.finalize_all_visible()
        tracker_instance.print_usage()
        tracker_instance.write_usage_json()
    print("FastAPI shutting down, tracker finalized.")

# Register lifecycle event handlers
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

@app.get("/usage", tags=["HTTP"], summary="Get current usage data")
def get_usage():
    """
    Returns the current usage data from the ActiveTabTracker in JSON format.
    """
    return tracker_instance.total_times

@app.get("/usage_json", tags=["HTTP"], summary="Get usage data from file")
def get_usage_json():
    """
    Returns the persisted usage data from tab_usage.json, if it exists.
    """
    try:
        with open("tab_usage.json", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": "Could not read JSON file", "details": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that streams usage data in real time.
    Connect to ws://<host>:<port>/ws to receive JSON updates.
    """
    await websocket.accept()
    print("WebSocket client connected.")
    try:
        while True:
            # Send the current usage data every second (polling approach).
            usage_data = tracker_instance.total_times

            # Send the usage data as JSON
            await websocket.send_json(usage_data)

            # Sleep briefly before sending the next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()

