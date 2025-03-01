from ultralytics import YOLO
import time
import cv2
from utilities import *

model = YOLO('yolo11n-pose.pt')
phone_detector = YOLO('yolov8n.pt')

def get_standard(image_file):
    "Input image by file name"
    image = cv2.imread(image_file)
    image = cv2.resize(image, (640, 384))
    
    standard = model(image, show=False, save=False)
    with open("pose_output.txt", "w") as file:
        for std in standard:
            keypoints = std.keypoints.xy
            for kp in keypoints:
                nose_std = kp[0]  # Nose (index 0)
                left_eye_std = kp[1] # Left Eye
                right_eye_std = kp[2] # Right Eye
                left_shoulder_std = kp[5]  # Left Shoulder (index 5)
                right_shoulder_std = kp[6]  # Right Shoulder (index 6)

                # Standard parameters
                _, y_std = shoulders_to_nose(left_shoulder_std, right_shoulder_std, nose_std)
                y_tolerance = 0.15 * y_std
                angle_std = shoulder_angle(left_shoulder_std, right_shoulder_std)
                eye_std = eyes_distance(left_eye_std, right_eye_std)
                file.write(f"eye_std: {eye_std}, y_std: {y_std}, angle_std: {angle_std}\n")
    cv2.destroyAllWindows()
    return y_std, eye_std, angle_std, y_tolerance

def frame_processing(frame, y_std, eye_std, angle_std, y_tolerance, eye_tolerance=0.3, angle_tolerance=4):
    results = model(frame)
    
    for result in results:
        keypoints = result.keypoints.xy
        for kp in keypoints:
            if kp.numel() == 0:
                continue
            nose = kp[0] # Nose (index 0)
            left_eye = kp[1] # Left Eye (index 1)
            right_eye = kp[2] # Right Eye (index 1)
            left_shoulder = kp[5]  # Left Shoulder (index 5)
            right_shoulder = kp[6]  # Right Shoulder (index 6)
            
            _, y_dist = shoulders_to_nose(left_shoulder, right_shoulder, nose)
            eye_dist = eyes_distance(left_eye, right_eye)
            angle = shoulder_angle(left_shoulder, right_shoulder)
            
            y_state = y_distance_detection(y_dist, y_std, y_tolerance)
            wrong_dist = (not shoulder_detected(left_shoulder, right_shoulder))\
                or wrong_distance_detection(eye_dist, eye_std, eye_tolerance)
            leaning_state = lean_detection(angle, angle_std, angle_tolerance)
            
            # Uncommented for debugging purpose
            # label_text_1 = f"Humpbacked: {y_state}"
            # label_text_2 = f"Wrong dist.: {wrong_dist}, Leaning: {leaning_state}"
            
            # cv2.putText(frame, label_text_1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            # cv2.putText(frame, label_text_2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            # cv2.imshow("YOLOv11n-Pose Output", frame)
            frame = result.plot()
            return frame, y_state, wrong_dist, leaning_state
            
def phone_detection(frame):
    phone_using = False
    results = phone_detector(frame)
    for result in results:
        for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
            class_name = result.names[int(cls)]
            if class_name == "cell phone":
                phone_using = True
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Phone", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame, phone_using