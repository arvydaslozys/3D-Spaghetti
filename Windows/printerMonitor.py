from emailUtils import check_for_yes_reply, send_email, delete_all_emails_from_sender
from emailConfigurations import TO_EMAIL
#from detectionLoop import detectionLoop
from stopPrinter import stop_printer
#from printerConfig import PRINTER_IP
from getStatus import wait_for_print_start_ws

import cv2
import torch
import numpy as np
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'yolov5'))

from utils.general import non_max_suppression, scale_coords
from utils.augmentations import letterbox




class PrinterMonitor:
    def __init__(self, printer_name, printer_ip, camera_url, model,detection_count_threshold=15, consecutive_frames_threshold=5):
        self.printer_name = printer_name
        self.printer_ip = printer_ip
        self.camera_url = camera_url
        self.model = model
        self.print_started = False
        self.consecutive_count = 0
        self.detection_count_threshold = detection_count_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.prev_time = time.time()  # for FPS
        print(f"[{self.printer_name}] Connecting to camera: {self.camera_url}")
        self.cap = cv2.VideoCapture(self.camera_url)

    def wait_for_print_start(self):
        print(f"[{self.printer_name}] Waiting for print start...")
        #return wait_for_print_start_ws(self.printer_ip)
        return True

    def send_failure_email(self, frame):
        print(f"[{self.printer_name}] Sending failure email...")
        send_email(frame, self.printer_name)

    def check_email_reply(self, printer_name):
        print(f"[{self.printer_name}] Checking email reply...")
        return check_for_yes_reply(printer_name)

    def stop_printer(self):
        print(f"[{self.printer_name}] Stopping printer!")
        stop_printer(self.printer_ip)

    def cleanup(self):
        print(f"[{self.printer_name}] Cleaning up resources...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def process_one_frame(self):
        if not self.print_started:
            print(f"[{self.printer_name}] Waiting for print start...")
            self.print_started = self.wait_for_print_start()
            return False  # Skip detection until print starts

        ret, frame = self.cap.read()
        if not ret:
            print(f"[{self.printer_name}] Failed to read frame from stream.")
            return False

        # Preprocess
        img_resized = letterbox(frame, new_shape=640)[0]
        img = img_resized[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.model.device)
        img = img.float() / 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        with torch.no_grad():
            pred = self.model(img, augment=False)

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres=0.3, iou_thres=0.45)[0]

        detection_count = 0 if pred is None else len(pred)

        # Update consecutive detection logic
        if detection_count >= self.detection_count_threshold:
            self.consecutive_count += 1
        else:
            self.consecutive_count = 0

        if self.consecutive_count >= self.consecutive_frames_threshold:
            print(f"🚨 [{self.printer_name}] Failure condition met!")
            return True

        # Draw detections
        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], frame.shape).round()
            for *xyxy, conf, cls in pred:
                label = f'{int(cls)} {conf:.2f}'
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])),
                              (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show the video feed (optional)
        cv2.imshow(f'{self.printer_name} - Detection Feed', frame)

        # Calculate FPS
        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time

        print(
            f"[{self.printer_name}] detection count = {detection_count}, consecutive count = {self.consecutive_count} FPS = {fps:.2f}")
        return False


    def monitor(self):
        if self.wait_for_print_start():

            delete_all_emails_from_sender(TO_EMAIL)
            if self.monitor_detection_loop():
                ret, frame = self.cap.read()
                if not ret:
                    print(f"❌ [{self.printer_name}] Failed to capture image.")
                    return

                self.send_failure_email(frame)
                print(f"📤 [{self.printer_name}] Failure detected and email sent.")

                reply_received = False
                for attempt in range(20):
                    print(f"🔁 [{self.printer_name}] Checking reply ({attempt + 1}/20)...")
                    if self.check_email_reply():
                        self.stop_printer()
                        print(f"✅ [{self.printer_name}] Printer stopped!")
                        reply_received = True
                        break


                if not reply_received:
                    print(f"⏱️ [{self.printer_name}] No reply after 20 attempts.")

