from settings import settings

from utils.services import send_image_rfdetr, send_image_yolo26
import threading
import numpy as np
import cv2
import time

from utils.tools import draw_boxes_yolo26, calculate_score
from utils.protocols import PrinterProtocol, CameraProtocol
from typing import Protocol, TYPE_CHECKING, Optional
from utils.handle_failure import FailureHandler
from notifications.email_handler import PrinterAlertEmailHandler


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
                camera: CameraProtocol,
                printer: PrinterProtocol,

):

        self.printer = printer
        self.camera = camera

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
        #If user wishes to receive a notification, and then confirm the failure
        if settings.action_when_failure_detected is settings.FailureAction.SEND_COMMAND_AFTER_CONFIRMATION:

            if not self.printer_failed:
                self.printer_failed = True
                self.failurehandler = FailureHandler(self.last_frame,self.printer_name)
                thread = threading.Thread(target=self.failurehandler.handle_failure, args=())
                thread.start()
                return

            if self.failurehandler.response == 0:
                return

            if self.failurehandler.response == 1:
                if settings.printer_command_when_failure_detected is settings.PrinterCommand.STOP:
                    self.stop_print()
                elif settings.printer_command_when_failure_detected is settings.PrinterCommand.PAUSE:
                    self.pause_print()
                
                self.printer_failed = False
                del self.failurehandler

            elif self.failurehandler.response == 2:
                print("Sending the alert failed")
                self.printer_failed = False
                del self.failurehandler
                
        #If user only selects to stop the printer without sending a notification
        if settings.action_when_failure_detected is settings.FailureAction.SEND_COMMAND_IMMEDIATELY:
            if settings.printer_command_when_failure_detected is settings.PrinterCommand.STOP:
                self.stop_print()
            elif settings.printer_command_when_failure_detected is settings.PrinterCommand.PAUSE:
                self.pause_print()
            self.printer_failed = False

        #If user only selects to send a notification
        if settings.action_when_failure_detected is settings.FailureAction.ONLY_SEND_NOTIFICATION:
            if not self.printer_failed:
                self.printer_failed = True
                self.failurehandler = FailureHandler(self.last_frame,self.printer_name)
                thread = threading.Thread(target=self.failurehandler.handle_failure, args=(True,))
                thread.start()
            if self.failurehandler.response == 1:
                self.printer_failed = False
                del self.failurehandler
            if self.failurehandler.response == 2:
                self.printer_failed = False
                del self.failurehandler


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

    def get_frame(self) -> Optional[np.ndarray]:
        """
        Returns:
            numpy.ndarray
        """
        return self.camera.get_frame()

    def stop_print(self) -> Optional[bool]:
        print(f"[{self.printer_name}] Stopping printer!")
        self.printer.stop_print()

    def pause_print(self) -> Optional[bool]:
        print(f"[{self.printer_name}] Pausing printer!")
        self.printer.pause_print()


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
                self.score = 0
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

