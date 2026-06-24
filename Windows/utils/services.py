import cv2
import requests

API_URL_RFDETR = "http://localhost:8000/detect/rfdetr"  # change if needed
API_URL_YOL26 = "http://localhost:8001/detect/yolo26"


def send_image_rfdetr(frame):
    success, img_encoded = cv2.imencode(".jpg", frame)
    if not success:
        return 0, []

    try:
        response = requests.post(
            API_URL_RFDETR,
            files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")},
            timeout=0.5
        )

        if response.status_code != 200:
            return 0, []

        data = response.json()
        return data.get("count", 0), data.get("boxes", [])

    except requests.exceptions.RequestException:
        return 0, []

def send_image_yolo26(frame):
    success, img_encoded = cv2.imencode(".jpg", frame)
    if not success:
        return 0, []

    try:
        response = requests.post(
            API_URL_YOL26,
            files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")},
            timeout=0.1
        )

        if response.status_code != 200:
            return 0, []

        data = response.json()
        return data.get("count", 0), data.get("boxes", [])

    except requests.exceptions.RequestException:
        return 0, []


