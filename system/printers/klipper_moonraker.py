import requests

class KlipperMoonrakerPrinter:
    """
    Example ip: 192.168.1.100
    """


    def __init__(self,printer_ip: str, printer_name: str):
        if not isinstance(printer_ip,str):
            raise TypeError(f"The ip address provided ({printer_ip}) is not str")

        self.printer_name = printer_name
        self.printer_ip = printer_ip

    def is_printing(self) -> bool | None:
        """
        Return True only if the printer is actively printing. If printer is unreachable, the printing status is unknown, thus function returns None
        """

        try:
            response = requests.get(
                f"http://{self.printer_ip}/printer/objects/query",
                params={"webhooks": "", "virtual_sdcard": "", "print_stats": ""},
                timeout=1,
            )
            response.raise_for_status()
            result = response.json()
            state = result["result"]["status"]["print_stats"]["state"]

            if state == "printing":
                print(f"{self.printer_name} is printing")
            else:
                print(f"{self.printer_name} is not printing")

            return state == "printing"
        except Exception:
            print(f"{self.printer_name} is not online")
            return None


    def stop_print(self) -> bool | None:
        """
        Returns True if printer stopped successfully, otherwise returns False. If it cannot be confirmed that the print was stopped, the function returns None
        """
        RETRY_AMOUNT = 5
        feedback = None
        for _ in range(RETRY_AMOUNT):
            MOONRAKER_URL = f"http://{self.printer_ip}:7125/printer/gcode/script"
            payload = {"script": "M112"}
            resp = requests.post(MOONRAKER_URL, json=payload, timeout=5)
            feedback = self.is_printing()
            if feedback is False:
                print(f"{self.printer_name} stopped successfully.\n")
                return True
        if feedback is None:
            print(f"Cannot verify if {self.printer_name} was stopped!.\n")
            return None
        return False
