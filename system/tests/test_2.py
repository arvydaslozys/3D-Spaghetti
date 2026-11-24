import time
import cv2
import pytest
import threading
import numpy as np
from utils.printer_monitor import PrinterMonitor
from notifications.email_handler import PrinterAlertEmailHandler
from utils.protocols import PrinterProtocol
from typing import Protocol
from utils.handle_failure import FailureHandler
from camera.camera import KlipperMoonrakerCamera
from unittest.mock import Mock, call, MagicMock
from utils.logic_loop import logic_loop
from printers.klipper_moonraker import KlipperMoonrakerPrinter
import utils.tools as tools

email_handler = PrinterAlertEmailHandler()

failurehandler = FailureHandler(email_handler)
baseClass = KlipperMoonrakerPrinter("192.168.5.2","TEST")
camera = KlipperMoonrakerCamera("http://camera.local/stream")


@pytest.fixture()
def printer():

    printer = PrinterMonitor(
    printer_name="TEST",
    printer_type="klipper_moonraker",
    camera=camera,
    printer=baseClass,
    failureHandler=failurehandler
    )
    printer.last_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    return printer

def test_handle_failure(monkeypatch,printer):

    class FakeCamera:
        def get_frame(self):
            return None

    printer.camera = FakeCamera()

    monkeypatch.setattr(printer.failureHandler.notificationhandler,"check_for_user_response",Mock(return_value=True))
    stop_print = Mock()
    monkeypatch.setattr(KlipperMoonrakerPrinter,"stop_print",stop_print)

    send_alert = Mock()
    monkeypatch.setattr(printer.failureHandler.notificationhandler,"send_alert",send_alert)
    printer.printer_failed = True

    set_failure_status = Mock()
    monkeypatch.setattr(printer,"set_failure_status",set_failure_status)

    printer.failureHandler.handle_failure(printer)

    set_failure_status.assert_has_calls([
        call(True),
        call(False),
    ])
    stop_print.assert_called_once()
    send_alert.assert_called_once()

def test_send_alert_when_failed(monkeypatch,printer):
    monkeypatch.setattr(
        printer,
        "handle_failure",
        lambda: printer.failureHandler.handle_failure(printer),
    )
    monkeypatch.setattr(
        email_handler,
        "check_for_user_response",
        Mock(return_value=False),
    )
    monkeypatch.setattr(
        "utils.handle_failure.time.sleep",
        lambda _: None,
    )

    class fakeKlipperCamera():
        def __init__(self, printer_ip):
            self.camera_url = printer_ip

        def get_frame(self) -> "numpy.ndarray":
            return np.zeros((100, 100, 3), dtype=np.uint8)

    camera = fakeKlipperCamera("http://camera.local/stream")

    printer.camera=camera

    def fake_send_image(*args):
        return 10,None

    send_alert = Mock()
    monkeypatch.setattr(email_handler,"send_email",send_alert)

    monkeypatch.setattr("utils.printer_monitor.send_image_yolo26",fake_send_image)
    monkeypatch.setattr("utils.printer_monitor.send_image_rfdetr",fake_send_image)

    for _ in range(6):
        printer.process_one_frame(False)

    assert printer.score > 100
    send_alert.assert_called_once()

@pytest.mark.parametrize("value",[True,False])
def test_is_printing(monkeypatch,value,printer):
    monkeypatch.setattr(KlipperMoonrakerPrinter,"is_printing",Mock(return_value=value))
    assert printer.is_printing() == value

def test_stop_print(monkeypatch,printer):
    stop_print = Mock()
    monkeypatch.setattr(KlipperMoonrakerPrinter,"stop_print",stop_print)
    printer.stop_print()
    stop_print.assert_called_once()

def test_get_frame(monkeypatch,printer):
    get_frame = Mock()
    monkeypatch.setattr(KlipperMoonrakerCamera,"get_frame",get_frame)
    printer.get_frame()
    get_frame.assert_called_once()

@pytest.mark.parametrize("value",[5,6])
#When value is 5, printer.score will return 100 (5x10x2), which is not considered a failure.
#When value is 6, printer.score will return 120
def test_process_one_frame(monkeypatch,value,printer):
    def fake_send_image(*args):
        return 10,None
    def fake_handle_failure():
        printer.set_failure_status(True)

    monkeypatch.setattr(printer,"handle_failure",fake_handle_failure)
    monkeypatch.setattr("utils.printer_monitor.send_image_yolo26",fake_send_image)
    monkeypatch.setattr("utils.printer_monitor.send_image_rfdetr",fake_send_image)

    for _ in range(value):
        printer.process_one_frame(False)

    if value == 5:
        assert printer.printer_failed == False
    else:
        assert printer.printer_failed == True

def test_logic_loop1(monkeypatch,printer):

    printers=[printer]

    process_one_frame = Mock()
    printer.process_one_frame = process_one_frame

    monkeypatch.setattr(printer,"is_printer_online_check_due",Mock(return_value=False))
    monkeypatch.setattr(printer,"is_ready_for_monitoring",Mock(return_value=True))

    logic_loop(printers)

    process_one_frame.assert_called_once()

def test_logic_loop2(monkeypatch, printer):
    printers = [printer]

    process_one_frame = Mock()
    printer.process_one_frame = process_one_frame

    monkeypatch.setattr(printer, "is_printer_online_check_due", Mock(return_value=False))
    monkeypatch.setattr(printer, "is_ready_for_monitoring", Mock(return_value=False))

    logic_loop(printers)

    process_one_frame.assert_not_called()

@pytest.mark.parametrize("det1,det2,score,expected",    [
    (0, 100, 0, 90),
    (10, 10, 50, 70),
    (100, 0, 100, 190),
    (None, None, 100, 100),
    (10, 10, 0, 20),
    (None, None, 3, 3),
    (0, 0, 5, 0)
])
def test_calculate_score(det1,det2,score,expected):
    assert tools.calculate_score(score,det1,det2) == expected

@pytest.mark.parametrize("ret,frame,expected", [
(False, None, None),
(True, np.zeros((100, 100, 3), dtype=np.uint8), np.zeros((100, 100, 3), dtype=np.uint8))])
def test_KlipperMoonrakerCamera_get_frame(monkeypatch, ret, frame, expected):

    class FakeCapture:
        def read(self):
            return ret, frame

        def release(self):
            pass

    monkeypatch.setattr(cv2, "VideoCapture", lambda url: FakeCapture())

    camera = KlipperMoonrakerCamera("camera.local")

    result = camera.get_frame()
    
    if expected is None:
        assert result is None
    else:
        np.testing.assert_array_equal(result, expected)

def test_KlipperMoonrakerCamera_invalid_ip(monkeypatch):
    camera = KlipperMoonrakerCamera("111.111.111.111")
    result = camera.get_frame()
    assert result is None

def test_email_invalid_config(monkeypatch, printer):
    monkeypatch.setattr(email_handler,"SMTP_SERVER","TEST")
    printer.printer_failed = True
    printer.failureHandler.handle_failure(printer)
    assert printer.printer_failed == False