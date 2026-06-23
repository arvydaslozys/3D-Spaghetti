from utils.email_utils import check_for_yes_reply, send_email
from utils.stop_printer import stop_printer
from utils.services import send_image_rfdetr, send_image_yolo26
from utils.get_printing_status import is_printer_printing_ws
import cv2
import time
from utils.tools import draw_boxes_yolo26, calculate_score

#debug settings
TEST_IMAGE = False
TEST_VIDEO = False
SEND_EMAIL = False
CHECK_PRINTING_STATUS = True
CHECK_EMAILS = False
FAILURES_ENABLED = False

class PrinterMonitor:
    def __init__(self, printer_name, printer_ip, camera_url, printer_type):
        self.printer_name = printer_name
        self.printer_ip = printer_ip
        self.camera_url = camera_url
        self.fps_fps_prev_time = time.time()
        self.printer_type = printer_type
        self.score = 0
        self.is_printer_online_last_check = 0
        self.last_failure_check = 0
        self.print_started = False
        self.awaiting_reply = False
        self.camera_available = True
        self.printer_failed = False

    def get_frame(self):
        cap = cv2.VideoCapture(self.camera_url)
        ret, frame = cap.read()
        return ret, frame

    def get_failure_status(self):
        return self.printer_failed

    def set_failure_status(self, STATUS):
        self.printer_failed = STATUS

    def is_printer_printing(self):
        #-----DEBUG-----#
        if not CHECK_PRINTING_STATUS:
            return True
        #-----DEBUG-----#


        print(f"[{self.printer_name}] Checking print status...")
        self.print_started = is_printer_printing_ws(self.printer_ip, self.printer_type, self.printer_name)
        if not self.print_started:
            print(f"[{self.printer_name}] not printing.")
            try:
                cv2.destroyWindow(f"{self.printer_name}_YOLO26")
                cv2.destroyWindow(f"{self.printer_name}_RFDETR")
            except:
                pass
        else:
            return True


    def send_failure_email(self, frame):
        if SEND_EMAIL:
            print(f"[{self.printer_name}] Sending failure email...")
            send_email(frame, self.printer_name)

    def is_camera_available(self):
        cap = cv2.VideoCapture(self.camera_url)
        ret, _ = cap.read()
        cap.release()
        if not ret:
            print(f"[{self.printer_name}] Camera is not available")
            self.camera_available = False
            return False

        self.camera_available = True
        return True

    def check_email_reply(self, printer_name):
        if CHECK_EMAILS:
            print(f"[{self.printer_name}] Checking email reply...")
            return check_for_yes_reply(self.printer_name)
        else:
            return True

    def stop_printer(self, printer_ip, printer_type):
        print(f"[{self.printer_name}] Stopping printer!")
        stop_printer(self.printer_ip,printer_type)

    def process_one_frame(self,SHOW_DETECTIONS):
        if TEST_IMAGE:
            frame = cv2.imread("test.jpg")
        else:
            cap = cv2.VideoCapture(self.camera_url)
            ret, frame = cap.read()
            if not ret:
                print("Couldn't capture image")
                return False

        detection_count_yolo26, boxes_yolo26 = send_image_yolo26(frame)
        detection_count_rfdetr, boxes_rfdetr = send_image_rfdetr(frame)

        print(detection_count_yolo26)

        self.score = calculate_score(detection_count_yolo26, detection_count_rfdetr, self.score)

        current_time = time.time()
        fps = 1.0 / (current_time - self.fps_prev_time)
        self.fps_prev_time = current_time

        if SHOW_DETECTIONS:
            cv2.imshow(f"{self.printer_name}_RFDETR",draw_boxes_yolo26(frame.copy(), boxes_rfdetr))
            cv2.imshow(f"{self.printer_name}_YOLO26",draw_boxes_yolo26(frame.copy(), boxes_yolo26))

        print(f"[{self.printer_name}] failure score = {self.score}, FPS = {fps:.2f}")


        if self.score > 100:
            self.set_failure_status(True)




