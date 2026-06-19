import cv2
import requests

def draw_boxes_rfdetr(frame, boxes):
    h, w = frame.shape[:2]

    for box in boxes:
        y1, x1, y2, x2 = map(int, box)

        # Flip horizontally
        x1_flipped = w - x2
        x2_flipped = w - x1

        cv2.rectangle(
            frame,
            (x1_flipped, y1),
            (x2_flipped, y2),
            (0, 0, 255),
            2
        )

    return frame

def draw_boxes_yolo26(frame, boxes):
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)

        # Always red (since you only care about "fail")
        color = (0, 0, 255)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

    return frame

def set_led_state(state, pi_ip, led_pin):
    '''
    if state:
        requests.get(f"http://{pi_ip}:5000/setlighting/{led_pin}/on")
    else:
        requests.get(f"http://{pi_ip}:5000/setlighting/{led_pin}/off")
    '''

def is_camera_available(camera_id, printer_name):
    '''
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()

    if not ret:
        print(f"[{printer_name}] Couldn't capture image, check camera id!")
        return False

    return True
    '''
def calculate_score(detection_count_1, detection_count_2, score):

    if detection_count_1 < 5:
        score -= 10
    if detection_count_2 < 5:
        score -= 10

    if detection_count_1 >= 5:
        score += detection_count_1

    if detection_count_2 >= 5:
        score += detection_count_2

    if score < 0:
        score = 0

    return score


