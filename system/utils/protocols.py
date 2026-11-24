from typing import Protocol, TYPE_CHECKING
import numpy as np


class PrinterProtocol(Protocol):

    def stop_print(self) -> bool | None:
        ...

    def is_printing(self) -> bool | None:
        ...



class CameraProtocol(Protocol):

    def get_frame(self) -> np.ndarray | None:
        ...



class NotificationHandlerProtocol(Protocol):

    def send_alert(self, last_frame: np.ndarray, printer_name: str) -> None:
        ...

    def check_for_user_response(self, printer_name: str) -> bool:
        ...



class FailureHandlerProtocol(Protocol):
    def handle_failure(self) -> None:
        ...