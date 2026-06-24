from utils.email_utils import delete_all_emails_from_sender
import time

def handle_failure(printer):

    printer.awaiting_reply = True
    ret, frame = printer.get_frame()
    if not ret:
        print(f"[{printer.printer_name}] Failed to capture image.")

    delete_all_emails_from_sender()
    printer.send_failure_email(frame)

    print(f"[{printer.printer_name}] Failure detected and email sent.")

    reply_received = False

    for attempt in range(20):
        print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")
        if printer.check_email_reply(printer.printer_name):
            printer.stop_printer(printer.printer_ip, printer.printer_type)
            print(f" [{printer.printer_name}] received a reply, printer stopping")
            printer.print_started = False
            printer.set_failure_status(False)
            break
        time.sleep(5)

    if not reply_received:
        print(f"[{printer.printer_name}] No reply after 20 attempts, continuing printing")

    printer.set_failure_status(False)
    printer.awaiting_reply = False
