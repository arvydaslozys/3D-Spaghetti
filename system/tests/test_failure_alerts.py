from unittest.mock import Mock

import notifications.email_handler
from notifications.email_handler import PrinterAlertEmailHandler
from printers.klipper_moonraker import KlipperMoonrakerPrinter


def test_handle_failure_sends_one_alert(monkeypatch,printer,fake_camera):
    printer.camera = fake_camera()
    monkeypatch.setattr(PrinterAlertEmailHandler,"check_for_user_response",Mock(return_value=True))
    stop_print = Mock()
    monkeypatch.setattr(KlipperMoonrakerPrinter,"stop_print",stop_print)
    send_alert = Mock()
    monkeypatch.setattr(notifications.email_handler.PrinterAlertEmailHandler,"send_alert",send_alert)
    printer.printer_failed = False

    set_failure_status = Mock()
    monkeypatch.setattr(printer,"set_failure_status",set_failure_status)
    printer.handle_failure()

    #stop_print.assert_called_once()
    send_alert.assert_called_once()


def test_frame_processing_sends_one_alert_when_score_exceeds_threshold(monkeypatch,printer,fake_camera):

    send_alert = Mock()
    monkeypatch.setattr(notifications.email_handler.PrinterAlertEmailHandler,"send_alert",send_alert)
    monkeypatch.setattr(notifications.email_handler.PrinterAlertEmailHandler,"check_for_user_response",Mock(return_value=False),)
    monkeypatch.setattr(
        "utils.handle_failure.time.sleep",
        lambda _: None,
    )

    printer.camera=fake_camera()

    def fake_send_image(*args):
        return 10,None

    monkeypatch.setattr("utils.printer_monitor.send_image_yolo26",fake_send_image)
    monkeypatch.setattr("utils.printer_monitor.send_image_rfdetr",fake_send_image)

    for _ in range(6):
        printer.process_one_frame(False)

    send_alert.assert_called_once()


def test_printer_failure_flag_is_false_when_alert_sending_fails(monkeypatch, printer):
    monkeypatch.setattr(notifications.email_handler.PrinterAlertEmailHandler,"send_alert",Mock(return_value=False))
    printer.printer_failed = False
    printer.handle_failure()
    assert printer.printer_failed == False
