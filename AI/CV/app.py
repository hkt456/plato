# app.py (in AI/CV folder)
import cv2
import torch
import numpy as np
from ultralytics import YOLO

# Import your NumPy-based utilities
from AI.CV.utilities import (
    eyes_distance,
    shoulders_to_nose,
    shoulder_detected,
    shoulder_angle,
    lean_detection,
    wrong_distance_detection,
    y_distance_detection
)

# Load your YOLO models
model = YOLO('yolo11n-pose.pt')      # Pose detection
phone_detector = YOLO('yolov8n.pt')  # Object detection for phones

def get_standard(image_file):
    """
    Load an image, run YOLO pose, convert keypoints to NumPy,
    and compute posture reference metrics (y_std, eye_std, angle_std, y_tolerance).
    """
    image = cv2.imread(image_file)
    image = cv2.resize(image, (640, 384))
    
    results = model(image)  # Torch-based inference
    y_std, eye_std, angle_std, y_tolerance = 0, 0, 0, 0

    for r in results:
        keypoints = r.keypoints.xy  # Torch tensors
        for kp in keypoints:
            if kp.numel() == 0:
                continue
            # Convert Torch -> NumPy
            kp_np = kp.detach().cpu().numpy()

            nose_std          = kp_np[0]
            left_eye_std      = kp_np[1]
            right_eye_std     = kp_np[2]
            left_shoulder_std = kp_np[5]
            right_shoulder_std= kp_np[6]

            # NumPy-based geometry
            _, y_std_val = shoulders_to_nose(left_shoulder_std, right_shoulder_std, nose_std)
            angle_val    = shoulder_angle(left_shoulder_std, right_shoulder_std)
            eye_val      = eyes_distance(left_eye_std, right_eye_std)

            y_std        = y_std_val
            eye_std      = eye_val
            angle_std    = angle_val
            y_tolerance  = 0.15 * y_std  # example tolerance

    return y_std, eye_std, angle_std, y_tolerance

def phone_detection(frame):
    """
    Detect phones with YOLO. Draw bounding boxes around "cell phone" objects.
    Return (annotated_frame, phone_using_bool).
    """
    phone_using = False
    results = phone_detector(frame)
    for r in results:
        for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
            class_name = r.names[int(cls)]
            if class_name == "cell phone":
                phone_using = True
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Phone", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame, phone_using

def frame_processing(frame, y_std, eye_std, angle_std, y_tolerance,
                     eye_tolerance=0.3, angle_tolerance=4):
    """
    Process a single frame with YOLO pose, convert keypoints to NumPy,
    and return posture states plus the annotated frame.
    This version does NOT return immediately after the first keypoint.
    Instead, it processes all keypoints and returns the final state.
    """
    results = model(frame)

    # Default/fallback values if no keypoints found
    annotated_frame = frame
    final_y_state = False
    final_wrong_dist = False
    final_leaning_state = False

    for r in results:
        keypoints = r.keypoints.xy
        for kp in keypoints:
            if kp.numel() == 0:
                continue

            # Convert Torch -> NumPy
            kp_np = kp.detach().cpu().numpy()

            nose          = kp_np[0]
            left_eye      = kp_np[1]
            right_eye     = kp_np[2]
            left_shoulder = kp_np[5]
            right_shoulder= kp_np[6]

            # Compute posture geometry in NumPy
            _, y_dist = shoulders_to_nose(left_shoulder, right_shoulder, nose)
            eye_dist  = eyes_distance(left_eye, right_eye)
            angle     = shoulder_angle(left_shoulder, right_shoulder)

            # Compare to reference
            y_state = y_distance_detection(y_dist, y_std, y_tolerance)
            wrong_dist = (
                not shoulder_detected(left_shoulder, right_shoulder)
                or wrong_distance_detection(eye_dist, eye_std, eye_tolerance)
            )
            leaning_state = lean_detection(angle, angle_std, angle_tolerance)

            # Update final states if you want to reflect the last keypoint or any keypoint
            final_y_state = y_state
            final_wrong_dist = wrong_dist
            final_leaning_state = leaning_state

            # Overwrite annotated_frame each time or keep the last one
            annotated_frame = r.plot()

    # Return the final annotated frame and posture states
    return annotated_frame, final_y_state, final_wrong_dist, final_leaning_state

