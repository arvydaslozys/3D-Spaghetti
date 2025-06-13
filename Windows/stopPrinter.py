import websocket
import json

def stop_printer(printer_ip):
    ws_url = f"ws://{printer_ip}:9999"

    def on_open(ws):
        try:
            print(f"[{printer_ip}] Sending stop command...")
            ws.send(json.dumps({"method": "set", "params": {"stop": 1}}))
        except Exception as e:
            print(f"[{printer_ip}] Failed to send stop command: {e}")
        finally:
            ws.close()

    def on_error(ws, error):
        print(f"[{printer_ip}] WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"[{printer_ip}] WebSocket closed")

    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()  # optional timeout (in seconds)
    except Exception as e:
        print(f"[{printer_ip}] Could not connect to WebSocket: {e}")
