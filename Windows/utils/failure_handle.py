from utils.email_utils import delete_all_emails_from_sender
import time

def handle_failure(printer, frame):

    delete_all_emails_from_sender()
    #printer.send_failure_email(frame)

    print(f"[{printer.printer_name}] Failure detected and email sent.")

    reply_received = False

    for attempt in range(20):
        print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")
        if printer.check_email_reply(printer.printer_name):
            printer.stop_printer(printer.printer_ip, printer.printer_type)
            print(f" [{printer.printer_name}] Printer stopped!")
            printer.print_started = False
            printer.set_failure_status(False)
            break
        time.sleep(5)

    if not reply_received:
        print(f"[{printer.printer_name}] No reply after 20 attempts, continuing printing")

    printer.set_failure_status(False)
    printer.awaiting_reply = False
