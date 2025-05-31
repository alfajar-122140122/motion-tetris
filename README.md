# Motion Tetris - Tugas Besar Sistem/Teknologi Multimedia

![Motion Tetris Banner](link_ke_banner_anda.png) Selamat datang di **Motion Tetris**, sebuah proyek inovatif yang menggabungkan permainan klasik Tetris dengan teknologi multimedia interaktif! Proyek ini dikembangkan sebagai bagian dari Tugas Besar mata kuliah Sistem/Teknologi Multimedia. Motion Tetris memungkinkan pemain untuk mengontrol balok-balok Tetris menggunakan gerakan tangan yang dideteksi melalui kamera dengan teknologi MediaPipe, memberikan pengalaman bermain yang unik, menantang, dan menyenangkan.

---

## 📜 Deskripsi Proyek

Motion Tetris adalah implementasi game Tetris yang dimainkan bukan dengan keyboard atau mouse, melainkan dengan **deteksi gerakan tangan** pemain menggunakan teknologi **MediaPipe**. Mekanisme kontrolnya intuitif dan responsif:
* Pemain **mengangkat tangan kanan** untuk menggeser balok Tetris ke **kanan**.
* Pemain **mengangkat tangan kiri** untuk menggeser balok Tetris ke **kiri**.
* Pemain melakukan gestur **pinch** (seperti mencubit) untuk **merotasikan** balok Tetris.
* Pemain **menggenggam tangan** untuk melakukan **hard drop** (menjatuhkan balok dengan cepat).

Menggunakan kamera (webcam), program akan secara real-time memproses citra dan mengenali gestur tangan tersebut untuk mengendalikan permainan. Sistem deteksi gerakan telah dioptimalkan untuk memberikan respon yang cepat dan akurat.Proyek ini bertujuan untuk mengeksplorasi interaksi manusia-komputer melalui modalitas visual dan gerakan, serta mengaplikasikan konsep-konsep dalam teknologi multimedia untuk menciptakan pengalaman bermain yang imersif.

### ✨ Fitur Utama
* **Kontrol Gerakan Presisi**
  - Deteksi gerakan tangan real-time dengan MediaPipe
  - Gestur intuitif untuk setiap gerakan Tetris
  - Sistem anti-interference untuk mencegah deteksi yang tidak diinginkan
  - Optimasi performa untuk respon cepat
* **Gameplay Tetris Lengkap**
  - Semua gerakan klasik Tetris (gerak, rotasi, hard drop)
  - Sistem skor dan peningkatan level
  - Efek suara dan musik latar
  - Preview balok berikutnya
* **Antarmuka Interaktif**
  - Tampilan game board yang jelas
  - Feed kamera dengan overlay permainan
  - Panduan kontrol di layar
* **Fitur Tambahan**
  - Perekaman otomatis gameplay
  - Statistik permainan realtime

### 🛠️ Teknologi yang Digunakan
* **Bahasa Pemrograman:** Python
* **Library Computer Vision & Deteksi Pose/Tangan:** OpenCV, MediaPipe
* **Library GUI & Game Engine:** Pygame (atau Tkinter, PyQt, Kivy, dll.)
* **Library Pendukung:** NumPy (untuk operasi numerik)

## 👨‍💻 Tim Pengembang

| No. | Nama Lengkap        | NIM        | ID GitHub                                   |
| --- | ------------------- | ---------- | ------------------------------------------- |
| 1.  | Alfajar    | 122140122    | [@alfajar-122140122](https://github.com/alfajar-122140122) |
| 2.  | Muhammad Ghiffari Iskandar    | 122140189    | [@GhiffariIs](https://github.com/GhiffariIs) |

---

## 🚀 Instalasi

Untuk menjalankan program Motion Tetris di komputer Anda, ikuti langkah-langkah berikut:

### Prasyarat
* Python (versi 3.7 atau lebih baru direkomendasikan).
* `pip` (Python package installer).
* Webcam yang terhubung dan berfungsi dengan baik.
* (Sebutkan prasyarat lain jika ada, misal OS tertentu, library sistem tambahan).

### Langkah-langkah Instalasi
1.  **Clone Repositori**
    Buka terminal atau command prompt, lalu clone repositori ini:
    ```bash
    git clone https://github.com/alfajar-122140122/motion-tetris.git
    cd motion-tetris
    ```

2.  **(Opsional, tapi direkomendasikan) Buat dan Aktifkan Virtual Environment**
    ```bash
    python -m venv venv
    ```
    * Untuk Windows:
        ```bash
        venv\Scripts\activate
        ```
    * Untuk macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instal Dependensi**
    Instal semua library yang dibutuhkan menggunakan file `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Catatan: Pastikan Anda telah membuat file `requirements.txt` yang berisi semua library yang dibutuhkan, contoh: `opencv-python`, `mediapipe`, `pygame`, `numpy`)*

---

## 🎮 Cara Penggunaan

Setelah instalasi berhasil, Anda dapat menjalankan program sebagai berikut:

1.  Pastikan virtual environment (jika Anda menggunakannya) sudah aktif.
2.  Pastikan webcam Anda sudah terpasang dan tidak digunakan oleh aplikasi lain. Posisikan diri Anda agar tangan dapat terdeteksi dengan baik oleh kamera.
3.  Jalankan script utama program dari terminal:
    ```bash
    python main.py
    ```
    *(Ganti `main.py` dengan nama file eksekusi utama program Anda jika berbeda).*

4.  Jendela permainan akan muncul, dan kamera akan mulai mendeteksi gerakan tangan Anda.
5.  **Instruksi Bermain:**
    * **Menggerakkan Balok ke Kanan:** Angkat **tangan kanan** Anda di atas batas tinggi yang terdeteksi.
    * **Menggerakkan Balok ke Kiri:** Angkat **tangan kiri** Anda di atas batas tinggi yang terdeteksi.
    * **Memutar Balok:** Lakukan gestur **pinch** (mendekatkan ibu jari dan telunjuk).
    * **Hard Drop:** Genggam tangan (semua jari tertekuk) untuk menjatuhkan balok dengan cepat.
    * **Kontrol Keyboard Tambahan:**
      - **P:** Pause/Resume permainan
      - **Q:** Keluar dari permainan
      - **R:** Mulai ulang (saat game over)
      - **O:** Ubah mode tampilan (overlay/side-by-side)

6.  Tips untuk Deteksi Gerakan yang Optimal:
    * Pastikan pencahayaan ruangan cukup terang
    * Jaga jarak ±1 meter dari kamera
    * Tunjukkan gerakan dengan jelas dan konsisten
    * Hindari gerakan yang terlalu cepat

---

## 📅 Timeline Progress

### Minggu 1 
- Initial Commit: Setup awal project (6 Mei)
- Setup webcam dan frame capture (7 Mei)
- Instalasi MediaPipe dan konfigurasi dasar (7 Mei)
- Implementasi deteksi tangan dengan MediaPipe (7 Mei)
- Pengembangan kontrol gerakan tangan (8 Mei)
- Mapping gesture untuk gerak kiri/kanan dan rotasi (8 Mei)
- Peningkatan akurasi gesture clap (8 Mei)
- Implementasi board Tetris 10x20 (9 Mei)
- Penambahan kontrol dan bentuk Tetris (11 Mei)

### Minggu 2 
- Implementasi overlay Tetris pada webcam (17 Mei)
- Testing dan optimasi overlay

### Minggu 3 
- Implementasi sistem clear row dan scoring (23 Mei)
- Penambahan sound effect dan BGM (23 Mei)
- Implementasi code modularization (25 Mei)
- Penambahan fitur game recording (25 Mei)

### Minggu 4 

- Implementasi fitur fast drop (27 Mei)
- Perubahan fast drop menjadi hard drop (30 Mei)
- Penambahan rotation delay (30 Mei)
- Perbaikan sistem gesture (31 Mei)
- Motion Tetris Patch 1.0 (31 Mei)
- Cleaning code final (31 Mei)

---

Selamat mengembangkan dan bermain Motion Tetris! Jika ada pertanyaan atau kendala, silakan buat *issue* di repositori ini.