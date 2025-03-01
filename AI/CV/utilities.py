import numpy as np

def sec_to_min(t):
    s = ""
    mins = int(t / 60)
    if mins != 0:
        s += str(mins) + 'm'
    s += str(t % 60) + 's'
    return s

def eyes_distance(left_eye, right_eye):
    x1, y1 = left_eye
    x2, y2 = right_eye
    dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
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

def shoulder_detected(left_shoulder, right_shoulder, eps=1e-6):
    """
    If either shoulder is [0, 0] (within eps), treat it as 'not detected'.
    """
    zero_vec = np.array([0., 0.])
    left_is_zero = np.allclose(left_shoulder, zero_vec, atol=eps)
    right_is_zero = np.allclose(right_shoulder, zero_vec, atol=eps)
    return left_is_zero or right_is_zero

def shoulder_angle(left_shoulder, right_shoulder):
    x1, y1 = left_shoulder
    x2, y2 = right_shoulder
    angle = np.degrees(np.arctan2(np.abs(y2 - y1), np.abs(x2 - x1)))
    return angle

def lean_detection(shoulder_angle, angle_std, angle_tolerance):
    return np.abs(shoulder_angle - angle_std) >= angle_tolerance

def wrong_distance_detection(eye_dist, eye_std, eye_tolerance):
    ratio = np.abs(eye_dist / eye_std - 1)
    return ratio >= eye_tolerance

def y_distance_detection(y_dist, y_std, y_tolerance):
    return np.abs(y_dist - y_std) >= y_tolerance

