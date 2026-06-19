from fastapi import FastAPI, UploadFile, File
import numpy as np
import cv2
import time

from rfdetr import RFDETRMedium

app = FastAPI()

# ── CONFIG ─────────────────────────
MODEL_PATH = "checkpoint_best_ema.pth"
CLASS_NAMES = ["fail"]
THRESHOLD = 0.3
# ───────────────────────────────────

model = None


@app.on_event("startup")
def load_model():
    global model
    print("Loading RF-DETR model...")

    model = RFDETRMedium(pretrain_weights=MODEL_PATH)
    model.optimize_for_inference()

    print("Model loaded ✅")


@app.post("/detect/rfdetr")
async def detect(file: UploadFile = File(...)):

    # ── PREPROCESS ──────────────────
    t0 = time.perf_counter()

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Invalid image"}
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    t1 = time.perf_counter()

    # ── INFERENCE ───────────────────
    detections = model.predict(frame_rgb, threshold=THRESHOLD)

    t2 = time.perf_counter()

    # ── POSTPROCESS ─────────────────
    count = len(detections)
    fail_count = sum(1 for cid in detections.class_id if cid == 0)
    boxes = detections.xyxy.tolist() if count > 0 else []

    t3 = time.perf_counter()

    # ── SPEED REPORT ────────────────
    pre_ms   = (t1 - t0) * 1000
    infer_ms = (t2 - t1) * 1000
    post_ms  = (t3 - t2) * 1000
    h, w = frame_rgb.shape[:2]
    print(
        f"Speed: {pre_ms:.1f}ms preprocess, "
        f"{infer_ms:.1f}ms inference, "
        f"{post_ms:.1f}ms postprocess "
        f"per image at shape (1, 3, {h}, {w})"
    )

    return {"count": count, "fail_count": fail_count, "boxes": boxes}

# service start:
# uvicorn serviceRfdetr:app --host 0.0.0.0 --port 8000