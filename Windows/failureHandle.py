from emailUtils import delete_all_emails_from_sender
import time




def handle_failure(printer, frame):


    delete_all_emails_from_sender()
    printer.send_failure_email(frame)
    print(f"[{printer.printer_name}] Failure detected and email sent.")

    reply_received = False
    for attempt in range(20):
        print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")
        if printer.check_email_reply(printer.printer_name):
            printer.stop_printer()
            print(f" [{printer.printer_name}] Printer stopped!")
            printer.print_started = False
            break
        time.sleep(5)
    if not reply_received:
        print(f"[{printer.printer_name}] No reply after 20 attempts.")

    # Reset consecutive count after handling to avoid repeated triggers
    printer.consecutive_count = 0
    printer.awaiting_reply = False


'''

Debug

printers = []
for cfg in printer_configs:
    printer = PrinterMonitor(
        printer_name=cfg["printer_name"],
        printer_ip=cfg["printer_ip"],
        camera_url=cfg["camera_url"],
    )
    printers.append(printer)


img = cv2.imread("image.png")
handle_failure(printers[0],img)
'''