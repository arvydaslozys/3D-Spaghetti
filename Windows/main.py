from printerMonitor import PrinterMonitor
from printerConfig import printer_configs
from failureHandle import handle_failure
from yolox.exp import get_exp
from yolox.utils import fuse_model, postprocess
from yolox.models import YOLOX
import threading
import cv2
import torch
import sys
import os
import time





print("Shared model loaded.")




printers = []
for cfg in printer_configs:
    printer = PrinterMonitor(
        printer_name=cfg["printer_name"],
        printer_ip=cfg["printer_ip"],
        camera_url=cfg["camera_url"],
    )
    printers.append(printer)


CHECK_INTERVAL = 300

while True:
    current_time = time.time()

    for printer in printers:

        if current_time - printer.last_start_check > CHECK_INTERVAL:
            printer.last_start_check = current_time  # Update check time
            printer.print_started = printer.wait_for_print_start()
            if printer.print_started:
                print(f"[{printer.printer_name}] printing in progress")
            else:
                print(f"[{printer.printer_name}] printing NOT in progress")



        if not printer.awaiting_reply and printer.print_started:
            failure = printer.process_one_frame()
            cv2.waitKey(100)
            if failure:
                printer.awaiting_reply = True
                ret, frame = printer.cap.read()
                if not ret:
                    print(f"[{printer.printer_name}] Failed to capture image.")
                    continue
                printer.cleanup()
                thread = threading.Thread(target=handle_failure, args=(printer, frame))
                thread.start()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Stopping program...")
        break

