import cv2
import time

cap = cv2.VideoCapture("http://172.20.10.2:8080/?action=stream")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
frame_size = (1280, 720)
fps = 10  # 10 frames per second
out = cv2.VideoWriter('output2.avi', fourcc, fps, frame_size)

interval = 1.0 / fps  # Time between frames (0.1 sec for 10 FPS)
last_capture_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        if current_time - last_capture_time >= interval:
            last_capture_time = current_time
            frame = cv2.resize(frame, frame_size)
            out.write(frame)
            cv2.imshow('Recording at 10 FPS', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Recording stopped.")

cap.release()
out.release()
cv2.destroyAllWindows()
