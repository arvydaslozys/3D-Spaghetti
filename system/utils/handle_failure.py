import time

from utils.protocols import NotificationHandlerProtocol

from notifications.email_handler import PrinterAlertEmailHandler

NOTIFICATONHANDLERTYPE="email"

if NOTIFICATONHANDLERTYPE == "email":
    notificationhandler = PrinterAlertEmailHandler()


class FailureHandler:

    def __init__(self,
                 frame,
                 printer_name,
                 notificationhandler: NotificationHandlerProtocol = notificationhandler):

        self.frame = frame
        self.printer_name = printer_name
        self.notificationhandler = notificationhandler
        self.response = 0
        self.attempts = 20

    def handle_failure(self) -> None:
        RESPONSE_RECEIVED = 1
        SEND_ALERT_FAILED = 2

        #if alert fails to send
        if not self.notificationhandler.send_alert(self.frame, self.printer_name):
            #debug statement
            self.response = SEND_ALERT_FAILED
            return
            
        for attempt in range(self.attempts):
            #print(f"[{printer.printer_name}] Checking reply ({attempt + 1}/20)...")
            #-------USER CONFRIMS FAILURE------#
            if self.notificationhandler.check_for_user_response(self.printer_name):
                self.response = RESPONSE_RECEIVED
                break

            time.sleep(5)