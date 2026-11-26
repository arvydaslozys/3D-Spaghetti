import numpy as np
import pytest

from camera.camera import KlipperMoonrakerCamera
from printers.klipper_moonraker import KlipperMoonrakerPrinter
from utils.printer_monitor import PrinterMonitor

baseClass = KlipperMoonrakerPrinter("192.168.5.2","TEST")
camera = KlipperMoonrakerCamera("http://camera.local/stream")


@pytest.fixture()
def fake_camera():
    class FakeCamera():
        def __init__(self, printer_ip = "111.111.111.111"):
            self.camera_url = printer_ip

        def get_frame(self) -> "numpy.ndarray":
            return np.zeros((100, 100, 3), dtype=np.uint8)
    return FakeCamera

@pytest.fixture()
def printer():

    printer = PrinterMonitor(
    printer_name="TEST",
    camera=camera,
    printer=baseClass,
    )
    printer.last_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    return printer
