import cv2
import requests

def draw_boxes_rfdetr(frame, boxes):
    h, w = frame.shape[:2]

    for box in boxes:
        y1, x1, y2, x2 = map(int, box)

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

        color = (0, 0, 255)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

    return frame



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


