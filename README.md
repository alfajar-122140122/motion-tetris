# Motion Tetris - Tugas Besar Sistem/Teknologi Multimedia

![Motion Tetris Banner](link_ke_banner_anda.png) Selamat datang di **Motion Tetris**, sebuah proyek inovatif yang menggabungkan permainan klasik Tetris dengan teknologi multimedia interaktif! Proyek ini dikembangkan sebagai bagian dari Tugas Besar mata kuliah Sistem/Teknologi Multimedia. Motion Tetris memungkinkan pemain untuk mengontrol balok-balok Tetris menggunakan gerakan tangan yang dideteksi melalui kamera dengan teknologi MediaPipe, memberikan pengalaman bermain yang unik, menantang, dan menyenangkan.

---

## 📜 Deskripsi Proyek

Motion Tetris adalah implementasi game Tetris yang dimainkan bukan dengan keyboard atau mouse, melainkan dengan **deteksi gerakan tangan** pemain menggunakan teknologi **MediaPipe**. Mekanisme kontrolnya intuitif:
* Pemain **mengangkat tangan kanan** untuk menggeser balok Tetris ke **kanan**.
* Pemain **mengangkat tangan kiri** untuk menggeser balok Tetris ke **kiri**.
* Pemain melakukan gestur **menepuk tangan (clap)** untuk **merotasikan** balok Tetris.

Menggunakan kamera (webcam), program akan secara real-time memproses citra dan mengenali gestur tangan tersebut untuk mengendalikan permainan. Proyek ini bertujuan untuk mengeksplorasi interaksi manusia-komputer melalui modalitas visual dan gerakan, serta mengaplikasikan konsep-konsep dalam teknologi multimedia untuk menciptakan pengalaman bermain yang imersif.

### ✨ Fitur Utama
* Gameplay Tetris klasik yang adiktif.
* Kontrol permainan intuitif menggunakan deteksi gerakan tangan (geser kanan/kiri, rotasi) melalui webcam dengan MediaPipe.
* Deteksi gerakan secara real-time.
* Antarmuka pengguna yang interaktif menampilkan papan permainan dan feed kamera (opsional, bisa juga hanya feedback visual di game).
* Sistem skor dan peningkatan level permainan.
* (Tambahkan fitur spesifik lainnya jika ada, seperti: *soft drop*, *hard drop* dengan gestur lain, pratinjau balok berikutnya, dll.)

### 🛠️ Teknologi yang Digunakan
* **Bahasa Pemrograman:** Python
* **Library Computer Vision & Deteksi Pose/Tangan:** OpenCV, MediaPipe
* **Library GUI & Game Engine:** Pygame (atau Tkinter, PyQt, Kivy, dll.)
* **Library Pendukung:** NumPy (untuk operasi numerik)
* (Sebutkan teknologi spesifik lainnya yang Anda gunakan)

---

## 👨‍💻 Tim Pengembang

| No. | Nama Lengkap        | NIM        | ID GitHub                                   |
| --- | ------------------- | ---------- | ------------------------------------------- |
| 1.  | [Alfjar]    | [122140122]    | [@alfajar-122140122](https://github.com/alfajar-122140122) |
| 2.  | [Muhammad Ghiffari Iskandar]    | [122140189]    | [@GhiffariIs](https://github.com/GhiffariIs) |

---

## 📖 Logbook Project Steps

Berikut adalah catatan progress dan update proyek setiap progressnya.


| Progress Ke- | Kontributor           | Aktivitas/Progress                                                                                                                                                             | Status                                                                                                                              | Note                                                                       |
| :--------: | :--------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| 1 | Alfajar | Setup awal webcam & baca frame | Done |  |
| 2 | Ghiffari | Tambah deteksi tangan (gesture) | Done | Bisa optimasi lebih lanjut agar performance tidak boros |
| 3 | Alfajar | Mapping gesture → kontrol: Kanan/kiri/tepuk = kontrol tetris | Done | Perbaiki nanti aja pas udah ada tetrisnya |
| 4 | Ghiffari | Buat board/grid Tetris: Matriks 10x20 siap tampung block | Done | Mengecilkan webcam agar di atasnya bisa dibuat board skor |
| 5 | Alfajar | Bikin bentuk Tetris (shape): Shape (L, I, T, Z, dll) dalam array | Done |  |
| 6 | Alfajar | Gerak otomatis + gesture kontrol: Block turun otomatis, bisa digeser | Done | Butuh Optimasi soalnya masih buruk banget |
| 7 | Alfajar | Tambah rotasi saat tepuk tangan: Gesture tepuk → trigger rotate | Done | Butuh Optimasi Logika tepuk tangannya, sering miss detection kalau mengepalkan tangan |
| 8 | Alfajar | Overlay Tetris di webcam: Game di-render di atas video webcam | Done | aman harusnya tapi looksnya jadi kecil banget, ntar di rescale |
| 9 | Ghiffari | Tambah skor & line clear: Tetris bisa clear row & hitung skor | Done |  |
| 10 | Ghiffari | Tambah Sound sfx | Done |  |
| 11 | Alfajar | Simpan video output (opsional): Rekam sesi jadi .mp4 | Done |  |
| 12 | Alfajar | Clean code & refactor | Done |  |
| 13 | Ghiffari | Fix Rotation dan Gesture Optimization: Memberikan delay pada logika rotasi dan memperbaiki pendeteksi gesture tangan | Done |  |
| 14 | Alfajar & Ghiffari | Laporan Akhir: Membuat Laporan Akhir di LaTex | Ongoing |  |

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
    cd [NAMA_REPOSITORI_ANDA]
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
    * **Menggerakkan Balok ke Kanan:** Angkat **tangan kanan** Anda hingga melewati batas ketinggian tertentu yang terdeteksi.
    * **Menggerakkan Balok ke Kiri:** Angkat **tangan kiri** Anda hingga melewati batas ketinggian tertentu yang terdeteksi.
    * **Memutar Balok:** Lakukan gestur **menepuk kedua tangan (clap)** di depan kamera.
    * **(Opsional) Mempercepat Jatuh (Soft Drop):** [Jika diimplementasikan, deskripsikan gerakannya, misal: Turunkan kedua tangan secara bersamaan].
    * **(Opsional) Menjatuhkan Langsung (Hard Drop):** [Jika diimplementasikan, deskripsikan gerakannya, misal: Gerakan tangan dengan cepat ke bawah atau gestur lain].

6.  Cobalah untuk mendapatkan skor tertinggi! Untuk keluar dari permainan, [Deskripsikan cara keluar, misal: tekan tombol 'ESC' atau tutup jendela permainan].

---

Selamat mengembangkan dan bermain Motion Tetris! Jika ada pertanyaan atau kendala, silakan buat *issue* di repositori ini.