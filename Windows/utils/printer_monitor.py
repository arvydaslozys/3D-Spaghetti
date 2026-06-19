from email_utils import check_for_yes_reply, send_email
from Windows.utils.stop_printer import stop_printer
from Windows.utils.services import send_image_rfdetr, send_image_yolo26
from get_printing_status import is_printer_printing_ws
import cv2
import time
from Windows.utils.tools import draw_boxes_yolo26, set_led_state, calculate_score

#debug settings
TEST_IMAGE = True
TEST_VIDEO = True
SEND_EMAIL = False
CHECK_PRINTING_STATUS = False
CHECK_EMAILS = False
FAILURES_ENABLED = False

class PrinterMonitor:
    def __init__(self, printer_name, printer_ip, camera_id, pi_ip, printer_type, led_pin):
        self.printer_name = printer_name
        self.printer_ip = printer_ip
        self.camera_id = camera_id
        self.last_start_check = 0
        self.print_started = False
        self.awaiting_reply = False
        self.camera_available = True
        self.consecutive_count = 0
        self.prev_time = time.time()
        #print(f"[{self.printer_name}] Connecting to camera: {self.camera_id}")
        self.led_pin = led_pin
        self.pi_ip = pi_ip
        self.printer_type = printer_type
        self.led_State = False
        self.set_led(self.led_State)
        self.score = 0

    def get_frame(self):
        cap = cv2.VideoCapture(self.camera_id)
        ret, frame = cap.read()
        return ret, frame

    def is_printer_printing(self):
        if not CHECK_PRINTING_STATUS:
            return True


        print(f"[{self.printer_name}] Checking print status...")
        self.print_started = is_printer_printing_ws(self.printer_ip, self.printer_type, self.printer_name)

        if self.print_started:
            return True

        else:
            print(f"[{self.printer_name}] not printing.")
            try:
                cv2.destroyWindow(f"{self.printer_name}_YOLO26")
                cv2.destroyWindow(f"{self.printer_name}_RFDETR")
            except:
                pass

        return False


    def send_failure_email(self, frame):
        if SEND_EMAIL:
            print(f"[{self.printer_name}] Sending failure email...")
            send_email(frame, self.printer_name)

    def check_email_reply(self, printer_name):
        if CHECK_EMAILS:
            print(f"[{self.printer_name}] Checking email reply...")
            return check_for_yes_reply(self.printer_name)
        else:
            return True

    def stop_printer(self, printer_ip, printer_type):
        print(f"[{self.printer_name}] Stopping printer!")
        stop_printer(self.printer_ip,printer_type)

    def set_led(self, state):
        set_led_state(state, self.pi_ip, self.led_pin)

    def process_one_frame(self,SHOW_DETECTIONS):
        if TEST_IMAGE:
            frame = cv2.imread("bambufail.jpeg")
        else:
            cap = cv2.VideoCapture(self.camera_id)
            ret, frame = cap.read()
            if not ret:
                print("Couldn't capture image")
                return False


        detection_count_yolo26, boxes_yolo26 = send_image_yolo26(frame)
        detection_count_rfdetr, boxes_rfdetr = send_image_rfdetr(frame)

        print(detection_count_yolo26)

        self.score = calculate_score(detection_count_yolo26, detection_count_rfdetr, self.score)

        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time

        if SHOW_DETECTIONS:
            cv2.imshow(f"{self.printer_name}_RFDETR",draw_boxes_yolo26(frame.copy(), boxes_rfdetr))
            cv2.imshow(f"{self.printer_name}_YOLO26",draw_boxes_yolo26(frame.copy(), boxes_yolo26))

        print(f"[{self.printer_name}] failure score = {self.score}, FPS = {fps:.2f}")


        if not FAILURES_ENABLED:
            return False

        if self.score > 100:
            self.score = 0
            return True

        return False




