from utils.printer_monitor import PrinterMonitor
from notifications.email_handler import PrinterAlertEmailHandler
from printers.klipper_moonraker import KlipperMoonrakerPrinter
from utils.handle_failure import FailureHandler
from camera.camera import KlipperMoonrakerCamera
import json
from pathlib import Path






def init_printers() -> list[PrinterMonitor] :
    configurations_dir = Path(__file__).resolve().parent.parent / "configurations"
    config_path = configurations_dir / "printer_configurations.json"
    with config_path.open(encoding="utf-8") as file:
        data = json.load(file)

    printermonitors = []

    notification_handler = PrinterAlertEmailHandler()

    for printers in data["printers"]:

        failurehandler = FailureHandler(notification_handler)
        printer = None
        camera = None
        printer_name = printers["printer_name"]
        printer_ip = printers["printer_ip"]
        printer_type = printers["printer_type"]
        camera_type = printers["camera"]["type"]
        if camera_type.upper() == "USB":
            camera_idx = printers["camera"]["idx"]


        if camera_type.upper() == "NETWORK" and printer_type.upper() == "KLIPPER_MOONRAKER":
            camera = KlipperMoonrakerCamera(printer_ip)
        else:
            raise ValueError(f"Unsupported camera type: {camera_type}")


        if printer_type.upper() == "KLIPPER_MOONRAKER":
            printertype = KlipperMoonrakerPrinter(printer_ip,printer_name)
        else:
            raise ValueError(f"Unsupported printer type: {printer_type}")


        printer = PrinterMonitor(
            printer_name = printer_name,
            printer_type = printer_type,
            camera = camera,
            printer = printertype,
            failureHandler = failurehandler
        )

        printermonitors.append(printer)


    return printermonitors




