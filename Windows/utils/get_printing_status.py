import websocket
import json
import threading
import requests


def is_printer_printing_ws(printer_ip,  printer_type, printer_name, timeout=5) -> bool:

    if printer_type.lower() == "creality_k1c":

        ws_url = f"ws://{printer_ip}:9999"
        result = {"started": False}

        def on_message(ws, message):
            try:
                data = json.loads(message)

                if "state" in data:
                    state_val = data["state"]
                else:
                    # Try nested inside params or result, depending on format
                    state_val = (
                        data.get("params", {}).get("state") or
                        data.get("result", {}).get("state")
                    )

                if state_val == 1:  # printing
                    print("Printer state is 'printing' (1)")
                    result["started"] = True
                    ws.close()

            except Exception as e:
                print("Error parsing message:", e)

        def on_open(ws):
            ws.send(json.dumps({
                "method": "get",
                "params": ["state"]
            }))

        ws_app = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message
        )

        thread = threading.Thread(target=ws_app.run_forever)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            ws_app.close()
            thread.join()

        return result["started"]

    elif printer_type == "klipper_moonraker":

        try:
            url = f"http://{printer_ip}:7125/printer/objects/query"
            payload = {
                "objects": {
                    "print_stats": ["state"]
                }
            }


            resp = requests.post(url, json=payload, timeout=3)
            data = resp.json()
            state = data.get("result", {}).get("status", {}).get("print_stats", {}).get("state", "unknown")
            if state.lower() == "printing":
                return True
            else:
                return False
        except:
            print(f"Printer [{printer_name}] not online/unreachable")
            return False

    return False

