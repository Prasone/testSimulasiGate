# 🚗 Gate Simulation Indonesia

Sistem simulasi gerbang parkir Indonesia dengan deteksi plat nomor otomatis menggunakan computer vision dan RFID.

---

## 📋 Fitur Utama

### 1. **Deteksi Plat Nomor Otomatis (ALPR)**
   - Mendeteksi dan membaca plat nomor kendaraan secara real-time
   - Menggunakan OCR (Optical Character Recognition)
   - Tampilan hasil deteksi plat dalam format yang jelas

### 2. **Kontrol Gerbang RFID**
   - **Gate IN**: Sistem masuk gerbang dengan RFID UID
   - **Gate OUT**: Sistem keluar gerbang dengan RFID UID
   - Validasi RFID untuk kontrol akses

### 3. **Live Camera Feed**
   - Streaming video langsung dari kamera
   - Menampilkan hasil deteksi plat secara real-time di atas video

### 4. **Riwayat Transaksi**
   - Pencatatan setiap transaksi masuk dan keluar
   - Melihat history lengkap semua aktivitas gerbang

### 5. **Web Interface Modern**
   - Interface yang user-friendly dan responsive
   - Gradient design yang menarik
   - Animasi smooth untuk better UX

---

## 🛠️ Teknologi & Library yang Digunakan

### Backend
| Teknologi | Deskripsi |
|-----------|-----------|
| **Python** | Bahasa pemrograman utama |
| **Flask** | Web framework untuk membuat REST API dan web application |
| **OpenCV** | Library untuk computer vision dan video processing |
| **Pytesseract** | OCR engine untuk membaca teks dari gambar plat nomor |
| **Imutils** | Utility functions untuk image processing |
| **Numpy** | Array dan numerical computing |
| **Pillow** | Image processing library |
| **Threading** | Multi-threading untuk proses paralel |

### Frontend
| Teknologi | Deskripsi |
|-----------|-----------|
| **HTML5** | Struktur markup halaman web |
| **CSS3** | Styling dan layout dengan gradient, animations |
| **JavaScript** | Interaktivitas dan dynamic content |

### Hardware
| Perangkat | Deskripsi |
|----------|-----------|
| **Raspberry Pi** | Server komputer single-board (opsional) |
| **Webcam/USB Camera** | Untuk capture video feed |
| **RFID Reader** | Untuk membaca kartu RFID (simulasi dengan input manual) |

---

## 📦 Instalasi

### 1. Install Dependencies

**Windows/Mac:**
```bash
pip install -r requirements.txt
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-opencv
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Windows:**
- Download dari: https://github.com/UB-Mannheim/tesseract/wiki
- Install dan catat path instalasi

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### 3. Dependencies yang Diperlukan

File `requirements.txt` berisi:
```
flask
opencv-python
pytesseract
imutils
numpy
pillow
```

---

## 🚀 Cara Menjalankan

### 1. Setup Environment
```bash
cd testSimulasiGate
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
python app.py
```

### 4. Akses Web Interface
- Buka browser dan kunjungi: `http://localhost:5000`
- Atau sesuai dengan port yang ditampilkan di terminal

---

## 📁 Struktur Project

```
testSimulasiGate/
├── app.py                    # Main Flask application
├── plate_detector.py         # Module deteksi plat nomor
├── requirements.txt          # Dependencies list
├── test.py                   # Testing script
├── data/
│   ├── captures/            # Folder simpan screenshot
│   └── plates/              # Folder simpan hasil deteksi plat
├── static/
│   └── style.css            # CSS styling
└── templates/
    ├── index.html           # Halaman utama
    └── history.html         # Halaman riwayat
```

---

## 🎯 Cara Penggunaan

### 1. **Akses Halaman Utama**
   - Lihat live feed dari kamera
   - Lihat plat nomor yang terdeteksi secara real-time

### 2. **Gate IN**
   - Input RFID UID di form "Gate IN"
   - Klik tombol "RFID IN"
   - Sistem akan mencatat waktu masuk dan plat yang terdeteksi

### 3. **Gate OUT**
   - Input RFID UID di form "Gate OUT"
   - Klik tombol "RFID OUT"
   - Sistem akan mencatat waktu keluar

### 4. **Lihat History**
   - Klik tombol "📋 Lihat History"
   - Melihat semua transaksi yang tercatat (masuk/keluar)

---

## 🔧 Konfigurasi

### Mengatur Path Tesseract (Jika perlu)
Edit di `plate_detector.py`:
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Mengubah Port Flask
Edit di `app.py`:
```python
app.run(debug=True, port=5000)  # Ubah port sesuai kebutuhan
```

---

## 🐛 Troubleshooting

**Error: "tesseract is not installed"**
- Pastikan Tesseract OCR sudah terinstall dengan benar
- Setel path yang benar di konfigurasi

**Error: "Cannot open camera"**
- Periksa apakah kamera terhubung dengan benar
- Pastikan tidak ada aplikasi lain yang menggunakan kamera

**Error: "Module not found"**
- Pastikan sudah install semua requirements: `pip install -r requirements.txt`
- Aktifkan virtual environment dengan benar

---

## 📝 Metode Yang Digunakan

### 1. **Computer Vision (OpenCV)**
   - Real-time video capture dari webcam
   - Image preprocessing (grayscale, threshold, morphological operations)
   - Edge detection untuk identifikasi area plat

### 2. **Optical Character Recognition (OCR - Pytesseract)**
   - Ekstraksi text dari image plat nomor
   - Preprocessing image untuk meningkatkan akurasi OCR

### 3. **Web Framework (Flask)**
   - REST API endpoints untuk RFID IN/OUT
   - Server streaming video dengan Motion JPEG
   - Template rendering untuk dynamic content

### 4. **Database/Storage**
   - Simpan history transaksi (dapat dikembangkan dengan database)
   - Storage image untuk dokumentasi

### 5. **Multi-threading**
   - Video capture dan processing berjalan parallel
   - Tidak menghambat request web

---

## 🔐 Keamanan

- Input validation untuk RFID UID
- Database protection untuk history data
- Rate limiting untuk mencegah abuse

---

## 📈 Pengembangan Lebih Lanjut

- [ ] Integrasi database (MySQL/PostgreSQL)
- [ ] Authentication system
- [ ] SMS/Email notification
- [ ] Advanced Analytics & Report
- [ ] Mobile app integration
- [ ] AI-powered plate recognition
- [ ] Dual-camera system

---

## 👨‍💻 Author

Gate Simulation Indonesia Project

---

## 📞 Support

Untuk pertanyaan atau masalah, silakan buat issue di repository.

---

**Last Updated:** May 2026
