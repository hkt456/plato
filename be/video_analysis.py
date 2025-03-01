import cv2
import time
import threading
import base64
import json
import asyncio
import os
import sys

# Make sure we can import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the updated pose-detection functions (which no longer return early).
# These functions should be the "fixed" versions in AI/CV/app.py:
#   - get_standard(...)
#   - phone_detection(...)
#   - frame_processing(...)
from AI.CV.app import get_standard, phone_detection, frame_processing

class VideoAnalysis:
    """
    Encapsulates the logic for capturing video frames, processing posture/phone usage,
    and saving session summaries.
    """
    def __init__(self):
        # We'll store the latest webcam frame here and current states
        self.frame = None
        self.y_state = False
        self.wrong_dist = False
        self.leaning_state = False
        self.phone_using = False

    def capture_frames(self, cap, frame_lock):
        """
        Continuously capture frames from a webcam/video feed,
        resize them, and store the most recent frame in self.frame.
        """
        while True:
            ret, new_frame = cap.read()
            if not ret:
                break
            new_frame = cv2.resize(new_frame, (640, 384), interpolation=cv2.INTER_LINEAR)
            with frame_lock:
                self.frame = new_frame

    async def work_tracking(self, websocket, save_file="session_summary.json"):
        """
        Continuously process frames from the camera to detect posture/phone usage,
        and send them (as base64) to the client via the WebSocket.

        - The posture reference (y_std, eye_std, angle_std, y_tolerance) is obtained
          from 'standard_image.jpg' at the start of the session.
        - This loop runs indefinitely until the WebSocket is closed or an exception occurs.
        - Posture usage summaries are written to 'session_summary.json' at the end.
        """
        # 1) Get posture baseline from a standard image
        y_std, eye_std, angle_std, y_tolerance = get_standard("standard_image.jpg")

        # 2) Open the default camera (index 0). Change if you have multiple cameras.
        cap = cv2.VideoCapture(0)

        # 3) Start a separate thread to capture frames continuously
        frame_lock = threading.Lock()
        threading.Thread(
            target=self.capture_frames,
            args=(cap, frame_lock),
            daemon=True
        ).start()

        # 4) Initialize posture durations
        self.y_state, self.wrong_dist, self.leaning_state, self.phone_using = False, False, False, False
        y_duration, wrong_duration, leaning_duration, phone_duration = 0, 0, 0, 0

        # (Optional) If you want to limit session time, track start_session and do a while with a time check
        # For now, we'll run indefinitely until the WebSocket or camera fails.
        start_session = time.time()

        try:
            while True:
                # Small delay to avoid busy-looping
                await asyncio.sleep(0.01)
                start_time = time.time()

                with frame_lock:
                    if self.frame is None:
                        continue

                    # a) Detect phone usage in the current frame
                    processed_frame, self.phone_using = phone_detection(self.frame)

                    # b) Detect posture
                    #    'frame_processing' must be the version that does NOT return immediately
                    #    after the first keypoint (no early 'return').
                    processed_frame, self.y_state, self.wrong_dist, self.leaning_state = frame_processing(
                        processed_frame,
                        y_std, eye_std, angle_std, y_tolerance,
                        eye_tolerance=0.3,
                        angle_tolerance=4
                    )
                   

                    duration = time.time() - start_time

                    # c) Update posture durations
                    if self.y_state:
                        y_duration += duration
                    if self.wrong_dist:
                        wrong_duration += duration
                    if self.leaning_state:
                        leaning_duration += duration
                    if self.phone_using:
                        phone_duration += duration

                    # d) Draw debug text on the frame
                    label_text_1 = f"Humpbacked: {self.y_state} \t Phone using: {self.phone_using}"
                    label_text_2 = f"Wrong dist.: {self.wrong_dist}, \t Leaning: {self.leaning_state}"

                    cv2.putText(processed_frame, label_text_1, (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(processed_frame, label_text_2, (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # e) Encode the processed frame as JPEG -> base64 -> send via WebSocket
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    frame_data = base64.b64encode(buffer).decode()
                    await websocket.send_text(frame_data)

        except Exception as e:
            print(f"Connection closed: {e}")
        finally:
            # Release the camera resource
            cap.release()

        # 5) Save posture usage summary
        total_durations = {
            "Humpbacked": y_duration,
            "Wrong distance": wrong_duration,
            "Shoulder deviated": leaning_duration,
            "Phone usage": phone_duration
        }
        total_durations = {key: round(value, 3) for key, value in total_durations.items()}

        with open(save_file, "w") as file:
            json.dump(total_durations, file, indent=4)

    async def get_current_state(self):
        return self.y_state, self.wrong_dist, self.leaning_state, self.phone_using