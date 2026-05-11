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

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return None, None

    ret, frame = cap.read()

    cap.release()

    if not ret:
        return None, None

    # Detect plate
    plate_text, thresh = detect_plate(frame)

    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save image
    filename = f'static/captures/{timestamp}.jpg'

    cv2.imwrite(filename, frame)

    return plate_text, filename

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