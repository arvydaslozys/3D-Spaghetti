"""Check the camera and connection for every configured printer."""

#.venv/bin/python -m verify.setup


def verify_printers(printers):
    for printer in printers:
        frame = printer.get_frame()
        # PrinterMonitor.is_printing() converts an unreachable (None) status to False.
        status = printer.printer.is_printing()

        if frame is None:
            print(f"{printer.printer_name} camera is not working!")
        if status is None:
            print(f"{printer.printer_name} couldn't be reached!")
        if frame is not None and status is not None:
            print(f"{printer.printer_name} is ready!")


if __name__ == "__main__":
    import argparse
    from utils.initialize_printers import init_printers
    from notifications.email_handler import PrinterAlertEmailHandler

    parser = argparse.ArgumentParser("setup_test")
    parser.add_argument('--printers', dest='printers', type=str, help='set --printers flag to True if you want to test printer connections')
    parser.add_argument('--notifications', dest='notifications', type=str, help='set --notifications flag to True if you want to test notifications')
    args = parser.parse_args()

    if args.__getattribute__("printers") == "true":
        verify_printers(init_printers())
    if args.__getattribute__("notifications") == "true":
        #add notification testing
        pass

