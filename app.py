from flask import Flask, render_template, request, redirect
    plate_out, image = capture_plate()

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
        return 'Data RFID tidak ditemukan'

    plate_in = data[2]

    if plate_in != plate_out:
        conn.close()
        return f'Plat tidak cocok! IN={plate_in} OUT={plate_out}'

    cursor.execute('''
    UPDATE parking
    SET time_out=?, status='OUT'
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

    cursor.execute('SELECT * FROM parking ORDER BY id DESC')

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

    os.makedirs('static/captures', exist_ok=True)

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )