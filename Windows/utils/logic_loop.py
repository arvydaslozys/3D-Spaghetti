from utils.printer_monitor import PrinterMonitor
from configurations.printer_configurations import printer_configs
from utils.failure_handle import handle_failure
import threading
import cv2
import time
from utils.startup_display import hello

SHOW_DETECTIONS = True
PRINTER_ONLINE_CHECK_INTERVAL = 30
FAILURE_CHECK_INTERVAL = 1

def init_printers():
    printers = []
    for cfg in printer_configs:
        printer = PrinterMonitor(
            printer_name=cfg["printer_name"],
            printer_ip=cfg["printer_ip"],
            camera_url=cfg["camera_url"],
            printer_type=cfg["printer_type"]
        )
        printers.append(printer)
    return printers

def logic_loop(printers):
    current_time = time.time()

    for printer in printers:

        # checking if the printer is printing and if the camera is available every PRINTER_ONLINE_CHECK_INTERVAL
        if current_time - printer.is_printer_online_last_check > PRINTER_ONLINE_CHECK_INTERVAL:
            printer.is_printer_online_last_check = current_time  # Update check time

            # is the printer currently printing/online
            if not printer.get_printing_status():
                continue

            # is the camera available
            if not printer.is_camera_available():
                continue

        if not printer.awaiting_reply and printer.print_started and printer.camera_available:
            if current_time - printer.last_failure_check > FAILURE_CHECK_INTERVAL:
                printer.last_failure_check = current_time  # Update check time
                printer.process_one_frame(SHOW_DETECTIONS)
                cv2.waitKey(1)

                if printer.get_failure_status():
                    thread = threading.Thread(target=handle_failure, args=(printer,))
                    thread.start()
