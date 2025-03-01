import cv2
import time
import threading
import base64
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import asyncio

from app import *

app = FastAPI()

frame = None

def capture_frames(cap, frame_lock):
    global frame
    while True:
        ret, new_frame = cap.read()
        if not ret:
            break
        new_frame = cv2.resize(new_frame, (640, 384), interpolation=cv2.INTER_LINEAR)
        with frame_lock:  # Lock to prevent race conditions
            frame = new_frame

async def work_tracking(websocket: WebSocket, session_time=2700, save_file="session_summary.json"):
    # Get standard parameter
    y_std, eye_std, angle_std, y_tolerance = get_standard(image_file="standard_image.jpg")
    cap = cv2.VideoCapture(1)
    
    # Threading to increase speed
    frame_lock = threading.Lock()  # Thread lock for safe frame access
    threading.Thread(target=capture_frames, args=(cap, frame_lock), daemon=True).start()
    
    y_duration, wrong_duration, leaning_duration, phone_duration = 0, 0, 0, 0
    y_state, wrong_dist, leaning_state = False, False, False
    start_session = time.time()
    try:
        while time.time() - start_session <= session_time:
            await asyncio.sleep(0.05)
            start_time = time.time()
            with frame_lock:  # Lock to prevent race conditions
                if frame is None:
                    continue
                
                # processing the frame
                processed_frame, phone_using = phone_detection(frame)
                processed_frame, y_state, wrong_dist, leaning_state = frame_processing(processed_frame, y_std, eye_std, angle_std, y_tolerance, eye_tolerance=0.3, angle_tolerance=4)
                duration = time.time() - start_time
                if y_state:
                    y_duration += duration
                if wrong_dist:
                    wrong_duration += duration
                if leaning_state:
                    leaning_duration += duration
                if phone_using:
                    phone_duration += duration
                
                # Uncommented for debugging purpose
                label_text_1 = f"Humpbacked: {y_state} Phone using: {phone_using}"
                label_text_2 = f"Wrong dist.: {wrong_dist}, Leaning: {leaning_state}"
                
                cv2.putText(processed_frame, label_text_1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(processed_frame, label_text_2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
                _, buffer = cv2.imencode('.jpg', processed_frame)
                frame_data = base64.b64encode(buffer).decode()
                await websocket.send_text(frame_data)
            # return y_duration, wrong_duration, leaning_duration, phone_duration
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        cap.release()
    
    # Save output as .json file
    total_durations = {
        "Humpbacked": y_duration,
        "Wrong distance": wrong_duration,
        "Shoulder deviated": leaning_duration,
        "Phone usage": phone_duration
    }
    total_durations = {key: round(value, 3) for key, value in total_durations.items()}
    
    with open(save_file, "w") as file:
        json.dump(total_durations, file, indent=4)
        
@app.websocket("/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    await work_tracking(websocket, session_time=10)
    
JSON_FILE_PATH = "session_summary.json"
@app.get("/get_summary", response_class=FileResponse)
def get_summary():
    """API endpoint to return the session summary JSON file."""
    return JSON_FILE_PATH