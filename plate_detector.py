import cv2
import pytesseract
import numpy as np
import imutils


def detect_plate(frame):

    # =========================
    # PREPROCESS
    # =========================
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edged = cv2.Canny(blur, 100, 200)

    # =========================
    # FIND CONTOURS
    # =========================
    contours, _ = cv2.findContours(
        edged,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )[:20]

    plate = None

    # =========================
    # DETECT PLATE SHAPE
    # =========================
    for contour in contours:

        area = cv2.contourArea(contour)

        if area < 2000:
            continue

        peri = cv2.arcLength(contour, True)

        approx = cv2.approxPolyDP(
            contour,
            0.02 * peri,
            True
        )

        # Rectangle detection
        if len(approx) == 4:

            x, y, w, h = cv2.boundingRect(approx)

            ratio = w / float(h)

            # Ratio plat Indonesia
            if 2 < ratio < 6:
                plate = approx
                break

    # =========================
    # IF NO PLATE
    # =========================
    if plate is None:
        return None, None

    # =========================
    # CROP PLATE
    # =========================
    x, y, w, h = cv2.boundingRect(plate)

    plate_img = gray[y:y+h, x:x+w]

    # =========================
    # RESIZE
    # =========================
    plate_img = cv2.resize(
        plate_img,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # =========================
    # CLAHE
    # =========================
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    plate_img = clahe.apply(plate_img)

    # =========================
    # THRESHOLD
    # =========================
    _, thresh = cv2.threshold(
        plate_img,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # =========================
    # OCR CONFIG
    # =========================
    custom_config = (
        r'--oem 3 '
        r'--psm 7 '
        r'-c tessedit_char_whitelist='
        r'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )

    # =========================
    # OCR
    # =========================
    text = pytesseract.image_to_string(
        thresh,
        config=custom_config
    )

    # =========================
    # CLEAN TEXT
    # =========================
    text = ''.join(
        c for c in text
        if c.isalnum()
    )

    return text, thresh