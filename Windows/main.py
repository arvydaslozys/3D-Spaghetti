from printerMonitor import PrinterMonitor
from printerConfigurations import printer_configs
from failureHandle import handle_failure
import threading
import cv2
import time
from check_printer_online import is_printer_online
from startup_display import hello



hello()





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


            # is the printer turned on
            printer.printer_online = is_printer_online(printer.cap)
            if not printer.printer_online:
                printer.printer_online = False
                print(f"[{printer.printer_name}] Not online/Camera unavailable")
                continue

           # is the printer currently printing || stupid function name
            printer.print_started = printer.wait_for_print_start()
            if not printer.print_started:
                print(f"[{printer.printer_name}] Printing NOT in progress")
                continue


        if not printer.awaiting_reply and printer.print_started and printer.printer_online:
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
        print("Stopping program...")
        break

