import numpy as np
import torch

def sec_to_min(t):
    s = ""
    min = int(t / 60)
    if min != 0:
        s += str(min) + 'm'
    s += str(t % 60) + 's'
    return s

def eyes_distance(left_eye, right_eye):
    x1, y1 = left_eye
    x2, y2 = right_eye
    dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
    return dist

def shoulders_to_nose(left_shoulder, right_shoulder, nose):
    x1, y1 = left_shoulder
    x2, y2 = right_shoulder
    
    x_shoulder = (x1 + x2) / 2
    y_shoulder = (y1 + y2) / 2
    
    x_nose, y_nose = nose
    
    x_dist = np.abs(x_shoulder - x_nose)
    y_dist = np.abs(y_shoulder - y_nose)
    
    return x_dist, y_dist

def shoulder_detected(left_shoulder, right_shoulder):
    return torch.equal(left_shoulder, torch.tensor([0., 0.])) or torch.equal(right_shoulder, torch.tensor([0., 0.]))

# leaning shoulder
def shoulder_angle(left_shoulder, right_shoulder):
    x1, y1 = left_shoulder
    x2, y2 = right_shoulder

    # Compute angle in degrees
    angle = np.degrees(np.arctan2(np.abs(y2 - y1), np.abs(x2 - x1)))
    return angle

def lean_detection(shoulder_angle, angle_std, angle_tolerance):
    return np.abs(shoulder_angle - angle_std) >= angle_tolerance

def wrong_distance_detection(eye_dist, eye_std, eye_tolerance):
    ratio = np.abs(eye_dist/eye_std - 1)
    return ratio >= eye_tolerance

def y_distance_detection(y_dist, y_std, y_tolerance):
    return np.abs(y_dist - y_std) >= y_tolerance