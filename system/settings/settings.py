from enum import Enum

class FailureAction(Enum):
    ONLY_SEND_NOTIFICATION = "only_send_notification"
    SEND_COMMAND_AFTER_CONFIRMATION = "send_command_after_confirmation"
    SEND_COMMAND_IMMEDIATELY = "send_command_immediately"

class PrinterCommand(Enum):
    PAUSE = "pause"
    STOP = "stop"

printer_command_when_failure_detected = PrinterCommand.STOP
action_when_failure_detected = FailureAction.SEND_COMMAND_AFTER_CONFIRMATION

