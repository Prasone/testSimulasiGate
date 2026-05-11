from flask import Flask, render_template, request, redirect
import cv2
import sqlite3
import os
from datetime import datetime
from plate_detector import detect_plate

# =====================================
# FLASK
# =====================================
app = Flask(__name__)

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

# =====================================
# DATABASE
# =====================================
DB_NAME = 'database.db'

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
        time_in TEXT,
        time_out TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()


init_db()

# =====================================
# CAPTURE PLATE
# =====================================
def capture_plate():

    global camera

    ret, frame = camera.read()

    if not ret:
        return None, None

    # DETECT PLATE
    plate_text, thresh = detect_plate(frame)

    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save image
    filename = f'static/captures/{timestamp}.jpg'

    # Save full frame
    cv2.imwrite(filename, frame)

    return plate_text, 
    

# =====================================
# generate frame
# =====================================
def generate_frames():

    global camera

    while True:

        success, frame = camera.read()

        if not success:
            break

        # =========================
        # DETECT PLATE REALTIME
        # =========================
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        edged = cv2.Canny(blur, 100, 200)

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

            if len(approx) == 4:

                x, y, w, h = cv2.boundingRect(approx)

                ratio = w / float(h)

                if 2 < ratio < 6:

                    cv2.drawContours(
                        frame,
                        [approx],
                        -1,
                        (0, 255, 0),
                        3
                    )

                    break

        # Encode JPEG
        ret, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )

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

    return render_template('index.html')

# =====================================
# GATE IN
# =====================================
@app.route('/gate_in', methods=['POST'])
def gate_in():

    rfid = request.form['rfid']

    plate, image = capture_plate()

    if plate is None or plate == "":
        return 'Plat tidak terdeteksi'

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO parking (
        rfid,
        plate,
        image,
        time_in,
        status
    )
    VALUES (?, ?, ?, ?, ?)
    ''', (
        rfid,
        plate,
        image,
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

    rfid = request.form['rfid']

    # Capture ulang plat keluar
    plate_out, image = capture_plate()

    if plate_out is None or plate_out == "":
        return 'Plat keluar tidak terdeteksi'

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # Cari data kendaraan masuk
    cursor.execute('''
    SELECT * FROM parking
    WHERE rfid=? AND status='IN'
    ORDER BY id DESC
    LIMIT 1
    ''', (rfid,))

    data = cursor.fetchone()

    # RFID tidak ditemukan
    if data is None:
        conn.close()
        return 'Data RFID tidak ditemukan'

    plate_in = data[2]

    # Validasi plat
    if plate_in != plate_out:

        conn.close()

        return (
            f'''
            Plat tidak cocok!<br><br>

            Plat IN : {plate_in}<br>
            Plat OUT : {plate_out}
            '''
        )

    # Update data keluar
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
# RUN
# =====================================
if __name__ == '__main__':

    # Folder capture
    os.makedirs(
        'static/captures',
        exist_ok=True
    )

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )