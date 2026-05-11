from flask import Flask, render_template, request, redirect, Response
from flask import send_from_directory
import cv2
import sqlite3
import os
from datetime import datetime
from plate_detector import detect_plate

# =====================================
# FLASK
# =====================================
app = Flask(__name__)

# =====================================
# GLOBAL
# =====================================
latest_plate_text = ""
latest_frame = None
latest_plate_crop = None
last_detected_plate = ""
plate_counter = 0

# =====================================
# CAMERA
# =====================================
camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camera.isOpened():
    print("Camera gagal dibuka")
else:
    print("Camera berhasil dibuka")

# =====================================
# DATABASE
# =====================================
DB_NAME = 'data/database.db'

# =====================================
# INIT FOLDER
# =====================================
os.makedirs('data', exist_ok=True)
os.makedirs('data/captures', exist_ok=True)
os.makedirs('data/plates', exist_ok=True)

# =====================================
# INIT DATABASE
# =====================================
def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid TEXT,
        plate TEXT,
        image TEXT,
        plate_image TEXT,
        time_in TEXT,
        time_out TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()


init_db()

# =====================================
# GENERATE FRAMES
# =====================================
def generate_frames():

    global latest_plate_text
    global latest_frame
    global latest_plate_crop

    global last_detected_plate
    global plate_counter

    while True:

        success, frame = camera.read()

        if not success:
            continue

        display = frame.copy()

        # =========================
        # DETECT OCR
        # =========================
        plate_text, thresh = detect_plate(display)

        # =========================
        # STABILIZER OCR
        # =========================
        if plate_text:

            # Jika hasil sama
            if plate_text == last_detected_plate:

                plate_counter += 1

            else:

                # Reset counter
                plate_counter = 0
                last_detected_plate = plate_text

            # Harus stabil 3 frame
            if plate_counter >= 3:

                latest_plate_text = plate_text
                latest_frame = frame.copy()
                latest_plate_crop = thresh.copy()

        # =========================
        # DISPLAY TEXT
        # =========================
        cv2.putText(
            display,
            f"Plate: {latest_plate_text}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # =========================
        # ENCODE JPEG
        # =========================
        ret, buffer = cv2.imencode(
            '.jpg',
            display
        )

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )

# =====================================
# VIDEO FEED
# =====================================
@app.route('/video_feed')
def video_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =====================================
# HOME
# =====================================
@app.route('/')
def index():

    return render_template(
        'index.html',
        plate=latest_plate_text
    )

# =====================================
# GATE IN
# =====================================
@app.route('/gate_in', methods=['POST'])
def gate_in():

    global latest_plate_text
    global latest_frame
    global latest_plate_crop

    rfid = request.form['rfid']

    if latest_plate_text == "":
        return "Plat belum terdeteksi"

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # SAVE FULL IMAGE
    image_path = f'data/captures/{timestamp}.jpg'

    cv2.imwrite(
        image_path,
        latest_frame
    )

    # SAVE PLATE IMAGE
    plate_path = f'data/plates/{timestamp}.jpg'

    cv2.imwrite(
        plate_path,
        latest_plate_crop
    )

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO parking (
        rfid,
        plate,
        image,
        plate_image,
        time_in,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        rfid,
        latest_plate_text,
        image_path,
        plate_path,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'IN'
    ))

    conn.commit()
    conn.close()

    return redirect('/')

# =====================================
# GATE OUT
# =====================================
@app.route('/gate_out', methods=['POST'])
def gate_out():

    global latest_plate_text

    rfid = request.form['rfid']

    if latest_plate_text == "":
        return "Plat keluar belum terdeteksi"

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM parking
    WHERE rfid=? AND status='IN'
    ORDER BY id DESC
    LIMIT 1
    ''', (rfid,))

    data = cursor.fetchone()

    if data is None:
        conn.close()
        return "RFID tidak ditemukan"

    plate_in = data[2]

    # VALIDASI
    if plate_in != latest_plate_text:

        conn.close()

        return (
            f'''
            Plat tidak cocok!<br><br>

            Plat IN : {plate_in}<br>
            Plat OUT : {latest_plate_text}
            '''
        )

    cursor.execute('''
    UPDATE parking
    SET
        time_out=?,
        status='OUT'
    WHERE id=?
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        data[0]
    ))

    conn.commit()
    conn.close()

    return redirect('/')

# =====================================
# HISTORY
# =====================================
@app.route('/history')
def history():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM parking
    ORDER BY id DESC
    ''')

    data = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        data=data
    )

# =====================================
# SERVE IMAGE
# =====================================
@app.route('/captures/<filename>')
def captures(filename):

    return send_from_directory(
        'data/captures',
        filename
    )


@app.route('/plates/<filename>')
def plates(filename):

    return send_from_directory(
        'data/plates',
        filename
    )

# =====================================
# RUN
# =====================================
if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )