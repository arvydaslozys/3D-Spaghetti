from emailUtils import delete_all_emails_from_sender
from emailConfigurations import TO_EMAIL
import time

def handle_failure(printer, frame):
    delete_all_emails_from_sender(TO_EMAIL)
    printer.send_failure_email(frame)
    print(f"[{printer.printer_name}] Failure detected and email sent.")

    reply_received = False
    for attempt in range(20):
        print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")
        if printer.check_email_reply(printer.printer_name):
            printer.stop_printer()
            print(f" [{printer.printer_name}] Printer stopped!")
            printer.cleanup()
            printer.print_started = False
            break
        time.sleep(5)
    if not reply_received:
        print(f"[{printer.printer_name}] No reply after 20 attempts.")

    # Reset consecutive count after handling to avoid repeated triggers
    printer.consecutive_count = 0
    printer.awaiting_reply = False
