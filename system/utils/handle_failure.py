import time

from utils.protocols import NotificationHandlerProtocol


class FailureHandler:

    def __init__(self,notificationhandler: NotificationHandlerProtocol):
        self.notificationhandler = notificationhandler


    def handle_failure(self, printer):

        printer.set_failure_status(True)
        ATTEMPTS = 20

        #if alert fails to send
        if not self.notificationhandler.send_alert(printer.last_frame, printer.printer_name):
            printer.set_failure_status(False)
            return
            
        print(f"[{printer.printer_name}] Failure detected and email sent.")

        reply_received = False

        for attempt in range(ATTEMPTS):
            print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")

            if self.notificationhandler.check_for_user_response(printer.printer_name):
                print(f" [{printer.printer_name}] received a reply, attempting to stop")
                if printer.stop_print():
                    print(f"{printer.printer_name} stopped successfully!")

                printer.set_failure_status(False)
                reply_received = True
                break

            time.sleep(5)

        if not reply_received:
            print(f"[{printer.printer_name}] No reply after {ATTEMPTS} attempts, continuing printing")
            printer.set_failure_status(False)
