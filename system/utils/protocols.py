from typing import Protocol, TYPE_CHECKING


class PrinterProtocol(Protocol):

    def stop_print(self) -> None:
        ...

    def is_printing(self) -> bool:
        ...



class CameraProtocol(Protocol):

    def get_frame(self) -> "numpy.ndarray":
        ...



class NotificationHandlerProtocol(Protocol):

    def send_alert(self, last_frame: "numpy.ndarray", printer_name: str) -> None:
        ...

    def check_for_user_response(self, printer_name: str) -> bool:
        ...



class FailureHandlerProtocol(Protocol):
    def handle_failure(self) -> None:
        ...