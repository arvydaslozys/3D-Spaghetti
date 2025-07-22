def is_printer_online(cap):

    if cap is None or not cap.isOpened():
        return False
    else:
        return True