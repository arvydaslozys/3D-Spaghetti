from Windows.utils.printer_monitor import PrinterMonitor
from Windows.configurations.printer_configurations import printer_configs
from Windows.utils.failure_handle import handle_failure
import threading
import cv2
from Windows.utils.tools import is_camera_available
import time
from Windows.utils.startup_display import hello



hello()

printers = []
for cfg in printer_configs:
    printer = PrinterMonitor(
        printer_name=cfg["printer_name"],
        printer_ip=cfg["printer_ip"],
        camera_id=cfg["camera_id"],
        pi_ip=cfg["pi_ip"],
        printer_type=cfg["printer_type"],
        led_pin=cfg["led_pin"]
    )
    printers.append(printer)


CHECK_INTERVAL = 0.1
SHOW_DETECTIONS = True

while True:
    current_time = time.time()

    for printer in printers:

        if current_time - printer.last_start_check > CHECK_INTERVAL:
            printer.last_start_check = current_time  # Update check time


            # is the camera available
            printer.camera_available = is_camera_available(printer.camera_id, printer.printer_name)
            if not printer.camera_available:
                printer.set_led(False)
                continue
           # is the printer currently printing || stupid function name
            printer.print_started = printer.is_printer_printing()
            if not printer.print_started:
                printer.set_led(False)
                continue


        #if not printer.awaiting_reply and printer.print_started and printer.camera_available:
        if True:

            printer.set_led(True)
            failure = printer.process_one_frame(SHOW_DETECTIONS)
            cv2.waitKey(1)

            if failure:
            #if True:
                printer.set_led(False)
                printer.awaiting_reply = True
                ret, frame = printer.get_frame()
                if not ret:
                    print(f"[{printer.printer_name}] Failed to capture image.")
                    continue
                thread = threading.Thread(target=handle_failure, args=(printer, frame))
                thread.start()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Stopping program...")
        break

