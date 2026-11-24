from utils.services import send_image_rfdetr, send_image_yolo26
import threading
import numpy as np
import cv2
import time
from utils.tools import draw_boxes_yolo26, calculate_score
from utils.protocols import PrinterProtocol, CameraProtocol, FailureHandlerProtocol
from typing import Protocol, TYPE_CHECKING


#debug settings
TEST_IMAGE = False
SEND_EMAIL = True
CHECK_PRINTING_STATUS = True
CHECK_EMAILS = True

if TEST_IMAGE:
    print("WARNING, test image is enabled, camera won't be used!")
if not SEND_EMAIL:
    print("WARNING, email sending is disabled!")
if not CHECK_PRINTING_STATUS:
    print("WARNING, printer printing status won't be checked!")
if not CHECK_EMAILS:
    print("WARNING, email checking is disabled!")

class PrinterMonitor:
    def __init__(self, printer_name,
                 printer_type,
                 camera: CameraProtocol,
                 printer: PrinterProtocol,
                 failureHandler: FailureHandlerProtocol):

        self.printer = printer
        self.camera = camera
        self.failureHandler = failureHandler

        self.printer_name = printer_name
        self.fps_prev_time = time.time()
        self.score = 0
        self.is_printer_online_last_check = 0
        self.last_failure_check = 0
        self.print_started = False
        self.camera_available = True
        self.printer_failed = False
        self.last_frame = None

    def handle_failure(self) -> None:
        """
        Handles the failure in a new thread so that the function is non blocking for the main monitoring loop
        """
        thread = threading.Thread(target=self.failureHandler.handle_failure, args=(self,))
        thread.start()

    def get_failure_status(self) -> None:
        return self.printer_failed

    def set_failure_status(self, Status: bool) -> None:
        self.printer_failed = Status

    def is_ready_for_monitoring(self, Interval: int) -> bool:
        """
        Check whether the printer is ready for monitoring.
        Args:
            interval (int): Monitoring interval in seconds.
        Returns:
            bool: True if ready for monitoring, False otherwise.
        """
        if(not self.printer_failed
            and self.print_started
            and self.camera_available
            and self.is_process_one_frame_due(Interval)
        ):
            return True
        else:
            return False

    def is_printing(self) -> bool:
        self.print_started = self.printer.is_printing()

        if not self.print_started:
            try:
                cv2.destroyWindow(f"{self.printer_name}_YOLO26")
                cv2.destroyWindow(f"{self.printer_name}_RFDETR")
            except:
                pass
            return False
        else:
            return True

    def get_frame(self) -> np.ndarray | None:
        """
        Returns:
            numpy.ndarray
        """
        return self.camera.get_frame()

    def stop_print(self) -> None:
        print(f"[{self.printer_name}] Stopping printer!")
        self.printer.stop_print()

    def process_one_frame(self,SHOW_DETECTIONS: bool) -> None:
        if not self.printer_failed:
            if TEST_IMAGE:
                frame = cv2.imread("test.jpg")
            else:
                self.last_frame = self.camera.get_frame()

            detection_count_yolo26, boxes_yolo26 = send_image_yolo26(self.last_frame)
            detection_count_rfdetr, boxes_rfdetr = send_image_rfdetr(self.last_frame)

            print(detection_count_yolo26)

            self.score = calculate_score(self.score,detection_count_yolo26, detection_count_rfdetr)

            current_time = time.time()
            fps = 1.0 / (current_time - self.fps_prev_time)
            self.fps_prev_time = current_time

            if SHOW_DETECTIONS and self.last_frame is not None:
                cv2.imshow(f"{self.printer_name}_RFDETR",draw_boxes_yolo26(self.last_frame.copy(), boxes_rfdetr))
                cv2.imshow(f"{self.printer_name}_YOLO26",draw_boxes_yolo26(self.last_frame.copy(), boxes_yolo26))

            print(f"[{self.printer_name}] failure score = {self.score}, FPS = {fps:.2f}")


            if self.score > 100:
                self.handle_failure()

    def is_printer_online_check_due(self, interval: int) -> bool:

        diff = time.time() - self.is_printer_online_last_check
        if diff > interval:
            self.is_printer_online_last_check = time.time()
            return True
        else:
            return False

    def is_process_one_frame_due(self, interval: int) -> bool:

        diff = time.time() - self.last_failure_check
        if diff > interval:
            self.last_failure_check = time.time()
            return True
        else:
            return False

