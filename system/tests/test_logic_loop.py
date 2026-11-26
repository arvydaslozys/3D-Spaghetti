from unittest.mock import Mock

from utils.logic_loop import logic_loop


def test_logic_loop_processes_frame_when_printer_is_ready(monkeypatch,printer):

    printers=[printer]

    process_one_frame = Mock()
    printer.process_one_frame = process_one_frame

    monkeypatch.setattr(printer,"is_printer_online_check_due",Mock(return_value=False))
    monkeypatch.setattr(printer,"is_ready_for_monitoring",Mock(return_value=True))

    logic_loop(printers)

    process_one_frame.assert_called_once()


def test_logic_loop_skips_frame_when_printer_is_not_ready(monkeypatch, printer):
    printers = [printer]

    process_one_frame = Mock()
    printer.process_one_frame = process_one_frame

    monkeypatch.setattr(printer, "is_printer_online_check_due", Mock(return_value=False))
    monkeypatch.setattr(printer, "is_ready_for_monitoring", Mock(return_value=False))

    logic_loop(printers)

    process_one_frame.assert_not_called()
