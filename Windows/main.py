import torch
import time
import warnings
import cv2
from emailUtils import check_for_yes_reply, send_email, delete_all_emails_from_sender
from emailConfigurations import TO_EMAIL
from detectionLoop import detectionLoop
import torch
import pathlib
from stopPrinter import stop_printer
from printerConfig import PRINTER_IP
from getStatus import wait_for_print_start_ws
import sys
sys.path.append('./yolov5')  # Adjust path if yolov5 is in a different folder

# Patch WindowsPath to PosixPath
from models.common import DetectMultiBackend
from utils.torch_utils import select_device





warnings.filterwarnings("ignore", category=FutureWarning)

CONFIDENCE = 0.3

# Stop printer functions
def stop_printer1():
    print('spausdintuvas isjungtas')

print("✅ Script started")
device = select_device('0' if torch.cuda.is_available() else 'cpu')
model = DetectMultiBackend('best.pt', device=device)
model.eval()

# Create a VideoCapture object for webcam
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(f"http://{PRINTER_IP}:8080/?action=stream")


while True:
    #if wait_for_print_start_ws():
    if True:
        delete_all_emails_from_sender(TO_EMAIL)
        if detectionLoop(cap, model):

            # Capture an image from webcam
            ret, frame = cap.read()

            if not ret:
                print("❌ Failed to capture image.")
                continue

            send_email(frame)
            print("📤 Aptikta klaida, išsiųstas el. laiškas, laukiama atsakymo...")
            reply_received = False

            for attempt in range(20):  # Try 20 times
                print(f"🔁 Tikrinama atsakymo ({attempt + 1}/20)...")
                if check_for_yes_reply():
                    stop_printer()
                    cv2.destroyAllWindows()
                    print("✅ Atsakymas gautas. Spausdintuvas išjungtas.")
                    reply_received = True
                    break
                time.sleep(5)



            if reply_received:
                #continue to continue monitoring after print start
                break

            if not reply_received:
                print("⏱️ Atsakymo negauta per 20 bandymų. Grįžtama prie aptikimo.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 'q' pressed. Exiting loop.")
            cap.release()
            cv2.destroyAllWindows()
            exit()

    else:
        time.sleep(20)
        print("No print started yet..")

