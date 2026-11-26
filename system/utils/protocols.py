from typing import Protocol, TYPE_CHECKING, Optional
import numpy as np


class PrinterProtocol(Protocol):

    def stop_print(self) -> Optional[int]:
        ...

    def is_printing(self) -> Optional[int]:
        ...

    def pause_print(self) -> Optional[int]:
        ...



class CameraProtocol(Protocol):

    def get_frame(self) -> Optional[np.ndarray]:
        ...



class NotificationHandlerProtocol(Protocol):

    def send_alert(self, last_frame: np.ndarray, printer_name: str) -> None:
        ...

    def check_for_user_response(self, printer_name: str) -> bool:
        ...



class FailureHandlerProtocol(Protocol):
    def handle_failure(self) -> None:
        ...