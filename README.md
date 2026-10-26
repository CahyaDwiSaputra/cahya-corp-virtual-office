# CAHYA CORP — 3D Autonomous Multi-Agent Virtual Workspace

[![Three.js](https://img.shields.io/badge/Three.js-r128-black?logo=three.js)](https://threejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-slate)](https://github.com/CahyaDwiSaputra)

> **Kantor virtual 3D interaktif untuk visualisasi dan orkestrasi 8 profil AI Agent spesialis (Hermes Agent) secara otonom dan real-time.** Terinspirasi oleh arsitektur studio Skandinavia yang elegan dan konsep CLAW3D.

---

## 🌟 Fitur Utama

### 1. Smart Auto-Routing Orchestrator (Otomatis Tanpa Memanggil Nama Profil)
* Cukup ketik instruksi tugas apa saja dalam bahasa alami biasa di **Smart Command Bar**.
* Sistem secara cerdas mendeteksi kata kunci, domain teknis, dan intensi tugas secara instan (*zero-latency reactive NLP*).
* **Hanya karakter dengan jobdesk terkait yang akan bangkit dari area istirahat, berjalan menuju meja kerja, dan mengetik.** Karakter lain tetap santai menikmati waktu istirahat di lounge/pantry.

### 2. Live Synchronization Nyata (100% Real-Time Truth)
* **Bekerja (`Working`)**: Karakter berjalan ke meja kerjanya, duduk di kursi ergonomis, mengetik di keyboard mekanik, dan layar monitor ganda (*dual display*) aktif menampilkan baris kode.
* **Istirahat (`Idle`)**: Karakter berdiri dan keluyuran secara mandiri ke berbagai zona kantor:
  - ☕ **Pantry Espresso**: Menyeduh kopi segar di mesin espresso.
  - 🛋️ **Sofa Lounge**: Duduk santai membaca berita dan tren teknologi.
  - 📋 **Papan Kanban**: Berdiri memeriksa catatan tugas sprint di whiteboard.
  - 🌳 **Teras Jendela Kaca**: Menikmati pemandangan taman luar ruangan.
  - 💧 **Dispenser Air**: Mengambil air minum untuk hidrasi.
  - 💡 **Meja Rapat Bundar**: Duduk santai berdiskusi di meja tengah.

### 3. Kontrol 3D Lanjutan & Kebebasan Navigasi
* **Interactive Click-to-Move**: Klik agen mana pun, lalu klik titik lantai mana saja di kantor 3D untuk menggerakkannya secara manual dengan animasi ripple gelombang.
* **Kamera Pelacak Agen (`Follow Camera`)**: Kamera mengunci dan terbang mengikuti langkah karakter yang sedang berjalan.
* **Navigasi Terbang Kamera (WASD & Keyboard)**:
  - <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> / Tombol Panah: Geser kamera bebas melintasi ruangan studio.
  - <kbd>Q</kbd> / <kbd>E</kbd>: Putar sudut kamera secara dinamis.
  - <kbd>1</kbd>–<kbd>8</kbd>: Menerbangkan kamera langsung ke depan 8 spesialis.
  - <kbd>R</kbd>: Reset kamera ke sudut pandang ikhtisar.
  - <kbd>Spasi</kbd>: Menjeda (*pause*) atau melanjutkan simulasi.
* **Preset Suasana Pencahayaan Studio**:
  - ☀️ **Siang**: Pencahayaan daylight Skandinavia terang dan sejuk.
  - 🌇 **Senja (Golden Hour)**: Sinar matahari sore hangat dengan bayangan panjang sinematik.
  - 🌙 **Malam (Cozy Studio)**: Lampu sorot interior hangat dengan pendaran monitor.
* **Audio Synthesizer**: Efek suara tombol dan denting lonceng selesai (*chime*) menggunakan Web Audio API tanpa aset eksternal.
* **Terminal Konsol Log Studio (`📜 Log Studio`)**: Drawer transparan untuk memantau proses router AI dan status eksekusi masing-masing spesialis secara transparan.

---

## 👥 8 Profil Spesialis AI (Jobdesk Mapping)

| Profil | Karakter 3D | Spesialisasi & Tanggung Jawab Utama | Lokasi Meja |
| :--- | :--- | :--- | :--- |
| `pm` | **Tech Lead** | Product Requirement Document (PRD), WBS, Roadmap Sprint, Scope & Prioritas | Meja 1 (Kiri Atas) |
| `uiux` | **UI/UX Lead** | Wireframe, User Flow, Design Tokens (Figma), Layout Responsif, WCAG AA | Meja 2 (Tengah-Kiri Atas) |
| `frontend` | **Frontend Dev** | Next.js 15, React 19, TypeScript, Tailwind CSS, Client State & Interaktivitas | Meja 3 (Tengah-Kanan Atas) |
| `backend` | **Backend Dev** | Express, Node.js, FastAPI, REST/GraphQL API, JWT Auth, Redis Caching | Meja 4 (Kanan Atas) |
| `database` | **DB Architect** | PostgreSQL, MySQL, Prisma ORM, Drizzle, Skema Relasional, Migrasi & Indexing | Meja 5 (Kiri Bawah) |
| `devops` | **DevOps Eng** | Docker Multi-stage, GitHub Actions CI/CD, Nginx Proxy, SSL, Cloud Deploy | Meja 6 (Tengah-Kiri Bawah) |
| `qa` | **QA Specialist** | Automated E2E Testing (Playwright), Vitest, Integration Test, Test Case | Meja 7 (Tengah-Kanan Bawah) |
| `security` | **AppSec Lead** | OWASP Top 10, Validasi & Sanitasi Input, CSP/CORS Hardening, Dependency Audit | Meja 8 (Kanan Bawah) |

---

## 🚀 Cara Menjalankan

### Cara 1: Sekali Klik (Windows Launcher)
Cukup jalankan file batch:
```cmd
open-office.bat
```
Script akan otomatis memeriksa dan menjalankan bridge server (port `8090`) dan membuka browser Anda.

### Cara 2: Manual via Terminal
1. Jalankan bridge server:
   ```bash
   python server.py
   ```
2. Buka browser di alamat:
   ```text
   http://127.0.0.1:8090
   ```

### Cara 3: Melalui CLI Orkestrator (`cahya`)
Anda dapat memberikan tugas ke multi-agent langsung dari terminal mana pun:
```bash
# Otomatis dialokasikan ke Backend Dev & DB Architect:
cahya "buatkan sistem autentikasi login dan register pengguna"

# Otomatis dialokasikan ke Frontend Dev & UI/UX Lead:
cahya "perbaiki styling responsive navbar di mobile screen"

# Otomatis dialokasikan ke DB Architect:
cahya "optimasi query database dan buat index tabel orders"

# Otomatis dialokasikan ke seluruh 8 spesialis (Full Stack Project):
cahya "buatkan website e-commerce toko online lengkap"
```

---

## 📁 Struktur Repositori

```text
virtual-office/
├── index.html              # Aplikasi 3D Virtual Studio Utama (Standalone Three.js)
├── cahya-corp-3d.html       # Cadangan template antarmuka studio
├── server.py               # Advanced Bridge Server (HTTP/1.1, Smart Router & Chat Watcher)
├── status.json             # State persistence status 8 profil agen
├── open-office.bat         # Launcher mandiri satu-klik untuk Windows
├── update_status.py        # Helper sinkronisasi status proses hermes
├── libs/
│   ├── three.min.js        # Three.js library r128 (offline & lokal)
│   └── OrbitControls.js    # Three.js OrbitControls camera controller
└── README.md               # Dokumentasi lengkap proyek
```

---

## 🛠️ Teknologi yang Digunakan

* **Frontend 3D**: Three.js r128, OrbitControls, WebGL, Canvas API, Web Audio API
* **Backend Bridge**: Python 3 standard library (`http.server`, `socket`, `threading`, `sqlite3`, `subprocess`) — *zero external dependencies*
* **Multi-Agent Runtime**: Hermes Agent CLI & Profiles
* **Styling**: Modern Glassmorphism, Tailwind aesthetic, Inter & SFMono typography

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi **MIT** — bebas digunakan dan dikembangkan untuk keperluan riset maupun produksi.

Dibuat dengan ❤️ oleh **[CahyaDwiSaputra](https://github.com/CahyaDwiSaputra)** untuk ekosistem AI Multi-Agent.
