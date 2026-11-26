from unittest.mock import Mock

import pytest

import utils.handle_failure
from camera.camera import KlipperMoonrakerCamera
from printers.klipper_moonraker import KlipperMoonrakerPrinter


@pytest.mark.parametrize("value",[True,False])
def test_monitor_returns_printer_printing_status(monkeypatch,value,printer):
    monkeypatch.setattr(KlipperMoonrakerPrinter,"is_printing",Mock(return_value=value))
    assert printer.is_printing() == value


def test_monitor_delegates_stop_command_to_printer(monkeypatch,printer):
    stop_print = Mock()
    monkeypatch.setattr(KlipperMoonrakerPrinter,"stop_print",stop_print)
    printer.stop_print()
    stop_print.assert_called_once()


def test_monitor_requests_frame_from_camera(monkeypatch,printer):
    get_frame = Mock()
    monkeypatch.setattr(KlipperMoonrakerCamera,"get_frame",get_frame)
    printer.get_frame()
    get_frame.assert_called_once()


@pytest.mark.parametrize("value",[5,6])
#When value is 5, printer.score will return 100 (5x10x2), which is not considered a failure.
#When value is 6, printer.score will return 120
def test_monitor_flags_failure_only_when_score_exceeds_100(monkeypatch,value,printer):
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

def test_monitor_creates_one_failure_handler(monkeypatch, printer):
    constructor = Mock()
    monkeypatch.setattr("utils.printer_monitor.FailureHandler", constructor)
    monkeypatch.setattr("utils.printer_monitor.threading.Thread", Mock())

    printer.handle_failure()

    constructor.assert_called_once_with(printer.last_frame, printer.printer_name)