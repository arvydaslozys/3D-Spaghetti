import numpy as np
import cv2
import os
from ultralytics import YOLO

# ── CONFIG ─────────────────────────
MODEL_PATH = "best_yolo_scratch.pt"
THRESHOLD = 0.3
VIDEO_PATH = "timelapse_prusa_fail.avi"
OUTPUT_DIR = "video_results"
IMG_SIZE = 736
# ───────────────────────────────────


def load_model():
    print("Loading YOLO model...")
    model = YOLO(MODEL_PATH)
    print("Model loaded ✅")
    return model


def process_video(model, video_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}_result2_haa.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_idx = 0

    print("Processing video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ── YOLO inference ─────────────────────
        results = model.predict(frame, imgsz=IMG_SIZE, conf=THRESHOLD, verbose=False)
        result = results[0]

        output = frame.copy()

        boxes = []
        class_ids = []
        confidences = []

        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            confidences = result.boxes.conf.cpu().numpy()

        count = len(boxes)
        class_names = model.names

        # ── Draw detections ─────────────────────
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            cls = class_ids[i]
            conf = confidences[i]

            label = f"{class_names[cls]}: {conf:.2f}"

            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(output, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # ── TOP-LEFT COUNTER (NEW) ─────────────────────
        cv2.putText(
            output,
            f"Detections: {count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        # Save frame to video
        out.write(output)

        frame_idx += 2
        if frame_idx % 50 == 0:
            print(f"Processed {frame_idx} frames...")

    cap.release()
    out.release()

    print(f"\nSaved video → {output_path}")
    print(f"Total frames: {frame_idx}")


if __name__ == "__main__":
    model = load_model()
    process_video(model, VIDEO_PATH)