from emailUtils import check_for_yes_reply, send_email
from stopPrinter import stop_printer
from exps.custom.yolox_m import Exp
from getStatus import wait_for_print_start_ws
import cv2
import torch
import numpy as np
import time
import sys
import os
from yolox.exp import get_exp
from yolox.utils.visualize import vis
from yolox.utils import postprocess
from yolox.utils.visualize import vis
from predictor import Predictor  # If you put it in a new file


class PrinterMonitor:
    def __init__(self, printer_name, printer_ip, camera_url, detection_count_threshold=15, consecutive_frames_threshold=5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        exp = get_exp("YOLOX/exps/custom/yolox_m.py", None)
        exp.test_conf = 0.25
        exp.nmsthre = 0.45
        self.exp = Exp()

        self.model = exp.get_model()
        self.model.to(self.device)
        self.model.eval()

        ckpt_path = "20250715.pth"
        ckpt = torch.load(ckpt_path, map_location="cpu")
        self.model.load_state_dict(ckpt["model"])
        print(f"[{printer_name}] Loaded weights from {ckpt_path}")

        self.predictor = Predictor(
            model=self.model,
            exp=exp,
            cls_names=["failure"],
            decoder=None,
            device="cuda" if torch.cuda.is_available() else "cpu",
            fp16=False,
            legacy=False
        )

        self.printer_name = printer_name
        self.printer_ip = printer_ip
        self.camera_url = camera_url
        self.last_start_check = 0
        self.print_started = False
        self.awaiting_reply = False
        self.consecutive_count = 0
        self.detection_count_threshold = detection_count_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.prev_time = time.time()
        print(f"[{self.printer_name}] Connecting to camera: {self.camera_url}")
        self.cap = cv2.VideoCapture(self.camera_url)


    def wait_for_print_start(self):
        print(f"[{self.printer_name}] checking print status...")
        return True

    def send_failure_email(self, frame):
        print(f"[{self.printer_name}] Sending failure email...")
        send_email(frame, self.printer_name)

    def check_email_reply(self, printer_name):
        print(f"[{self.printer_name}] Checking email reply...")
        return check_for_yes_reply(self.printer_name)

    def stop_printer(self):
        print(f"[{self.printer_name}] Stopping printer!")
        stop_printer(self.printer_ip)

    def cleanup(self):
        window_name = f'{self.printer_name}'
        cv2.waitKey(1)
        print(f"Destroying window: {window_name}")
        cv2.destroyWindow(window_name)
        print(f"[{self.printer_name}] Resources cleaned")


    def process_one_frame(self):
        if not self.print_started:
            print(f"[{self.printer_name}] Waiting for print start...")
            self.print_started = self.wait_for_print_start()
            return False

        ret, frame = self.cap.read()
        if not ret:
            print(f"[{self.printer_name}] Failed to read frame from stream.")
            return False

        outputs, img_info = self.predictor.inference(frame)
        pred = outputs[0].cpu() if outputs[0] is not None else None
        detection_count = 0 if pred is None else len(pred)

        if detection_count >= self.detection_count_threshold:
            self.consecutive_count += 1
        else:
            self.consecutive_count = 0

        if self.consecutive_count >= self.consecutive_frames_threshold:
            print(f"[{self.printer_name}] Failure condition met!")
            return True

        result_frame = self.predictor.visual(outputs[0], img_info, cls_conf=0.1)
        cv2.imshow(f'{self.printer_name}', result_frame)

        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time

        print(
            f"[{self.printer_name}] detection count = {detection_count}, consecutive count = {self.consecutive_count}, FPS = {fps:.2f}")
        return False


