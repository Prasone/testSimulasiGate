import cv2
import pytesseract
import numpy as np
import re

# =====================================
# VALIDASI FORMAT PLAT INDONESIA
# =====================================
def is_valid_plate(text):

    # Contoh:
    # B1234XYZ
    # N1234AB
    # L1234AA

    pattern = r'^[A-Z]{1,2}[0-9]{1,4}[A-Z]{1,3}$'

    return re.match(pattern, text) is not None


# =====================================
# DETECT PLATE
# =====================================
def detect_plate(frame):

    # =========================
    # RESIZE FRAME
    # =========================
    frame = cv2.resize(
        frame,
        (640, 480)
    )

    display = frame.copy()

    # =========================
    # GRAYSCALE
    # =========================
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # =========================
    # NOISE REDUCTION
    # =========================
    blur = cv2.bilateralFilter(
        gray,
        11,
        17,
        17
    )

    # =========================
    # CONTRAST
    # =========================
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(blur)

    # =========================
    # EDGE DETECTION
    # =========================
    edged = cv2.Canny(
        contrast,
        100,
        200
    )

    # =========================
    # MORPHOLOGY
    # =========================
    kernel = np.ones((3, 3), np.uint8)

    edged = cv2.morphologyEx(
        edged,
        cv2.MORPH_CLOSE,
        kernel
    )

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
    )[:30]

    best_plate = None
    best_crop = None

    # =========================
    # FIND BEST RECTANGLE
    # =========================
    for contour in contours:

        area = cv2.contourArea(contour)

        # FILTER AREA
        if area < 2500:
            continue

        peri = cv2.arcLength(
            contour,
            True
        )

        approx = cv2.approxPolyDP(
            contour,
            0.02 * peri,
            True
        )

        # MUST RECTANGLE
        if len(approx) != 4:
            continue

        x, y, w, h = cv2.boundingRect(approx)

        ratio = w / float(h)

        # RATIO PLAT INDONESIA
        if ratio < 2 or ratio > 6:
            continue

        # SIZE FILTER
        if w < 100 or h < 30:
            continue

        # DRAW BOX
        cv2.drawContours(
            display,
            [approx],
            -1,
            (0, 255, 0),
            3
        )

        # CROP PLATE
        plate_img = gray[
            y:y+h,
            x:x+w
        ]

        # RESIZE OCR
        plate_img = cv2.resize(
            plate_img,
            None,
            fx=4,
            fy=4,
            interpolation=cv2.INTER_CUBIC
        )

        # OCR CLAHE
        plate_img = clahe.apply(plate_img)

        # ADAPTIVE THRESHOLD
        thresh = cv2.adaptiveThreshold(
            plate_img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # INVERT
        thresh = cv2.bitwise_not(thresh)

        # MORPH CLEAN
        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel
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

        # OCR
        text = pytesseract.image_to_string(
            thresh,
            config=custom_config
        )

        # CLEAN TEXT
        text = ''.join(
            c for c in text
            if c.isalnum()
        )

        text = text.upper()

        # VALIDATE
        if len(text) < 4:
            continue

        # VALIDATE INDONESIA FORMAT
        if not is_valid_plate(text):
            continue

        best_plate = text
        best_crop = thresh

        break

    return best_plate, best_crop