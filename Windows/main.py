from printerMonitor import PrinterMonitor
from printerConfig import printer_configs
from failureHandle import handle_failure
import threading
import cv2
import torch
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'yolov5'))

from models.common import DetectMultiBackend
from utils.torch_utils import select_device


device = select_device('0' if torch.cuda.is_available() else 'cpu')
model = DetectMultiBackend('best.pt', device=device)
model.eval()
print("Shared model loaded.")




printers = []
for cfg in printer_configs:
    printer = PrinterMonitor(
        printer_name=cfg["printer_name"],
        printer_ip=cfg["printer_ip"],
        camera_url=cfg["camera_url"],
        model=model
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
                thread = threading.Thread(target=handle_failure, args=(printer, frame))
                thread.start()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Stopping program...")
        break

