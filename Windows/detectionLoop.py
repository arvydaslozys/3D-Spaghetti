import cv2
import torch
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'yolov5'))

from utils.general import non_max_suppression, scale_coords
from utils.augmentations import letterbox

DETECTION_COUNT = 15
CONSECUTIVE_COUNT = 5


def detectionLoop(cap, model):
    consecutive_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from stream.")
                break

            # Preprocess with letterbox to maintain aspect ratio
            img_resized = letterbox(frame, new_shape=640)[0]
            img = img_resized[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).to(model.device)
            img = img.float() / 255.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            with torch.no_grad():
                pred = model(img, augment=False)

            # Apply NMS
            pred = non_max_suppression(pred, conf_thres=0.3, iou_thres=0.45)[0]

            detection_count = 0 if pred is None else len(pred)

            # Update consecutive detection logic
            if detection_count >= DETECTION_COUNT:
                consecutive_count += 1
            else:
                consecutive_count = 0

            if consecutive_count >= CONSECUTIVE_COUNT:
                return True

            # Draw detections
            if pred is not None and len(pred):
                pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], frame.shape).round()
                for *xyxy, conf, cls in pred:
                    label = f'{int(cls)} {conf:.2f}'
                    cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])),
                                  (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                    cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Show the video feed
            cv2.imshow('Detection Feed', frame)
            print(f"detection count = {detection_count}")

            # Break loop on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            cv2.waitKey(100)

    except KeyboardInterrupt:
        print("Detection loop stopped.")
