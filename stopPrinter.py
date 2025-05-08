import websocket
import json
from printerConfig import PRINTER_IP


def stop_printer(printer_ip=PRINTER_IP):
    ws_url = f"ws://{printer_ip}:9999"

    def on_open(ws):
        ws.send(json.dumps({"method": "set", "params": {"stop": 1}}))
        ws.close()

    websocket.WebSocketApp(ws_url, on_open=on_open).run_forever()
