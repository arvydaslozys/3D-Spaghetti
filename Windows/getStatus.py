import websocket
import json
import threading


def wait_for_print_start_ws(printer_ip, timeout=3) -> bool:
    """
    Subscribes to the general printer state updates (not print_stats).
    Returns True if state == 1 (printing) within the timeout.
    """
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
        # Optionally ask for status, depending on how your printer responds
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

