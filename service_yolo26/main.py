from fastapi import FastAPI, UploadFile, File
import numpy as np
import cv2
from ultralytics import YOLO

app = FastAPI()

# ── CONFIG ─────────────────────────
MODEL_PATH = "yolo26n_2026_03_31_736.pt"
THRESHOLD = 0.1
# ───────────────────────────────────

model = None

def scale_boxes(boxes, model_shape, frame_shape):
    model_h, model_w = model_shape
    frame_h, frame_w = frame_shape[:2]

    scale_x = frame_w / model_w
    scale_y = frame_h / model_h

    scaled = []
    for x1, y1, x2, y2 in boxes:
        scaled.append([
            x1 * scale_x,
            y1 * scale_y,
            x2 * scale_x,
            y2 * scale_y
        ])
    return scaled

@app.on_event("startup")
def load_model():
    global model
    print("Loading YOLO model...")

    model = YOLO(MODEL_PATH)

    print("Model loaded ✅")


@app.post("/detect/yolo26")
async def detect(file: UploadFile = File(...)):
    # Read uploaded image
    contents = await file.read()

    # Convert bytes → numpy array
    np_arr = np.frombuffer(contents, np.uint8)

    # Decode image
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Invalid image"}

    # Run inference (YOLO expects BGR, so no RGB conversion needed)
    results = model.predict(frame, imgsz=736 ,conf=0.03)

    result = results[0]

    # Get boxes
    if result.boxes is not None:
        boxes = result.boxes.xyxy.cpu().numpy().tolist()
        class_ids = result.boxes.cls.cpu().numpy().astype(int).tolist()
    else:
        boxes = []
        class_ids = []

    count = len(boxes)

    # Optional: count only class 0 (like "fail")

    return {"count": count, "boxes": boxes}

# Run with:
# uvicorn main:app --host 0.0.0.0 --port 8001