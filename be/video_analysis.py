import cv2
import time
import threading
import base64
import json
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# If your posture-detection methods come from a separate module, import them here:
# from app import get_standard, phone_detection, frame_processing
# Adjust as needed based on your project structure.
from AI.CV.app import get_standard, phone_detection, frame_processing


class VideoAnalysis:
    """
    Encapsulates the logic for capturing video frames, processing posture/phone usage,
    and saving session summaries.
    """
    def __init__(self):
        # We'll store the latest frame here
        self.frame = None

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

    async def work_tracking(self, websocket, session_time=2700, save_file="session_summary.json"):
        """
        Continuously process frames from the camera to detect posture/phone usage,
        and send them (as base64) to the client via the websocket.

        session_time: how long (in seconds) to run the tracking.
        save_file: where to store the posture usage summary as JSON.
        """
        # Get posture baseline from a standard image
        y_std, eye_std, angle_std, y_tolerance = get_standard(image_file="standard_image.jpg")
        cap = cv2.VideoCapture(1)

        # Use a lock to avoid race conditions while accessing self.frame
        frame_lock = threading.Lock()
        threading.Thread(target=self.capture_frames, args=(cap, frame_lock), daemon=True).start()

        # Initialize posture durations
        y_duration, wrong_duration, leaning_duration, phone_duration = 0, 0, 0, 0
        y_state, wrong_dist, leaning_state = False, False, False

        start_session = time.time()
        try:
            while time.time() - start_session <= session_time:
                await asyncio.sleep(0.05)
                start_time = time.time()

                with frame_lock:
                    if self.frame is None:
                        continue

                    # Process the current frame
                    processed_frame, phone_using = phone_detection(self.frame)
                    processed_frame, y_state, wrong_dist, leaning_state = frame_processing(
                        processed_frame, y_std, eye_std, angle_std, y_tolerance,
                        eye_tolerance=0.3, angle_tolerance=4
                    )

                    # Calculate how long this iteration took
                    duration = time.time() - start_time

                    # Update posture durations
                    if y_state:
                        y_duration += duration
                    if wrong_dist:
                        wrong_duration += duration
                    if leaning_state:
                        leaning_duration += duration
                    if phone_using:
                        phone_duration += duration

                    # Optional debug labels on the frame
                    label_text_1 = f"Humpbacked: {y_state} Phone using: {phone_using}"
                    label_text_2 = f"Wrong dist.: {wrong_dist}, Leaning: {leaning_state}"
                    cv2.putText(processed_frame, label_text_1, (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(processed_frame, label_text_2, (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # Encode the processed frame and send via WebSocket
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    frame_data = base64.b64encode(buffer).decode()
                    await websocket.send_text(frame_data)

        except Exception as e:
            print(f"Connection closed: {e}")
        finally:
            cap.release()

        # Save posture usage summary as JSON
        total_durations = {
            "Humpbacked": y_duration,
            "Wrong distance": wrong_duration,
            "Shoulder deviated": leaning_duration,
            "Phone usage": phone_duration
        }
        total_durations = {key: round(value, 3) for key, value in total_durations.items()}

        with open(save_file, "w") as file:
            json.dump(total_durations, file, indent=4)

