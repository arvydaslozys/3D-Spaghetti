from utils.printer_monitor import PrinterMonitor
import threading
import cv2
import time
from utils.startup_display import hello

SHOW_DETECTIONS = True
PRINTER_ONLINE_CHECK_INTERVAL = 5
PROCESS_ONE_FRAME_INTERVAL = 1



def logic_loop(printers):
    for printer in printers:
        # checking if the printer is printing and if the camera is available every PRINTER_ONLINE_CHECK_INTERVAL
        if printer.is_printer_online_check_due(PRINTER_ONLINE_CHECK_INTERVAL):

            #checks if the printer is currently printing. If not, sets the variable print_started to False. Then printer is skipped for monitoring until next check
            if not printer.is_printing():
                continue
        if printer.is_ready_for_monitoring(PROCESS_ONE_FRAME_INTERVAL):
            printer.process_one_frame(SHOW_DETECTIONS)
            cv2.waitKey(1)

