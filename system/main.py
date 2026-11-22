import cv2
from utils.startup_display import hello
from utils.logic_loop import logic_loop
from utils.initialize_printers import init_printers


if __name__ == "__main__":
    hello()

    printers = init_printers()

    while True:
        logic_loop(printers)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping program...")
            break

