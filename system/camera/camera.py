import cv2
from typing import Optional
import numpy as np

class UsbCamera:
    def __init__(self,camera_id):
        self.camera_id = camera_id

    def get_frame(self) -> Optional[np.ndarray]:
        cap = cv2.VideoCapture(self.camera_id)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            exit()

        ret, frame = cap.read()
        if ret:
            return frame
        else:
            print(f"Error: Could not read frame from camera_id - {self.camera_id}")

        cap.release()

class KlipperMoonrakerCamera:
    def __init__(self, printer_ip):
        self.camera_url = f"http://{printer_ip}/webcam/stream"
        self.cap = None

    def get_frame(self) -> Optional[np.ndarray]:
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_url)

        ret, frame = self.cap.read()
        if not ret:
            print(f"Could not read frame: {self.camera_url}")
            self.close()
            return None

        return frame

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None