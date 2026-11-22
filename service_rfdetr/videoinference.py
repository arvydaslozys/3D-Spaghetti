import numpy as np
import cv2
from rfdetr import RFDETRMedium
import os

# ── CONFIG ─────────────────────────
MODEL_PATH = "checkpoint_best_ema.pth"
CLASS_NAMES = ["fail"]
THRESHOLD = 0.3

VIDEO_PATH = " "
OUTPUT_DIR = "testing/video_results"
SAVE_FRAMES = False
# ───────────────────────────────────


def load_model():
    print("Loading RF-DETR model...")
    model = RFDETRMedium(pretrain_weights=MODEL_PATH)
    model.optimize_for_inference()
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
    output_video_path = os.path.join(OUTPUT_DIR, f"{base_name}_resultnaujas.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    frame_idx = 0

    print("Processing video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = model.predict(frame_rgb, threshold=THRESHOLD)

        output = frame.copy()

        count = len(detections)

        # ── Draw bounding boxes ─────────────────────
        if count > 0:
            boxes = detections.xyxy
            class_ids = detections.class_id
            confidences = detections.confidence

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box)
                class_id = class_ids[i]
                confidence = confidences[i]

                label = f"{CLASS_NAMES[class_id]}: {confidence:.2f}"

                cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(output, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # ── TOP LEFT COUNTER (NEW) ─────────────────────
        counter_text = f"Detections: {count}"

        cv2.putText(
            output,
            counter_text,
            (10, 30),  # top-left corner
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        # Write frame
        out.write(output)

        if SAVE_FRAMES:
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:06d}.jpg"), output)

        frame_idx += 2

        if frame_idx % 50 == 0:
            print(f"Processed {frame_idx} frames...")

    cap.release()
    out.release()

    print(f"\nSaved video → {output_video_path}")
    print(f"Total frames processed: {frame_idx}")


if __name__ == "__main__":
    model = load_model()
    process_video(model, VIDEO_PATH)