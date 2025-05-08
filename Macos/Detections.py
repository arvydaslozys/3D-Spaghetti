import torch
import time
import warnings
import cv2
import websocket
import json


#printer camera ip adress
stream_url = "http://172.20.10.2:8080/?action=stream"

number_of_detections = 10
number_of_frames_with_detections = 10
waiting_time_after_false_positive = 600  #10 minutes

#Function to stop the printer

def stop_printer(printer_ip="172.20.10.2"):
    ws_url = f"ws://{printer_ip}:9999"

    def on_open(ws):
        ws.send(json.dumps({"method": "set", "params": {"stop": 1}}))
        ws.close()
        sys.exit(0)

    websocket.WebSocketApp(ws_url, on_open=on_open).run_forever()


warnings.filterwarnings("ignore", category=FutureWarning)

# Load YOLOv5 model
model = torch.hub.load('./yolov5', 'custom', path='yolov5s.pt', source='local')


# Create a VideoCapture object
cap = cv2.VideoCapture(stream_url)

def detectionLoop():
    consecutive_count = 0
    try:
        while True:
            # Read the frame from the video stream
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from stream.")
                break

            # Run detection on the current frame
            results = model(frame)

            # Get detection count
            detection_count = len(results.pandas().xyxy[0])

            # Check if detection count is 5
            if detection_count >= number_of_detections:
                consecutive_count += 1
            else:
                consecutive_count = 0  # Reset counter if condition is not met

            # Print message if 5 consecutive detections meet the condition
            if consecutive_count == number_of_frames_with_detections:
                return True

            # Show the video feed (optional)
            cv2.imshow('Detection Feed', results.render()[0])  # Render detected frame

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    except KeyboardInterrupt:
        print("Detection loop stopped.")

while True:
    if detectionLoop() == True:
        print('Aptikta klaida, ar norite isjungti spausdintuva? Y/N')
        prompt = input()
        if prompt.lower() == 'y':
            stop_printer()
            print('Spausdintuvas Isjungtas')
            break
        else:
            time.sleep(waiting_time_after_false_positive)


# Release resources
cap.release()
cv2.destroyAllWindows()
