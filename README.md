# Simple Task / Project Tracker

Aplikasi manajemen tugas (_Task & Project Tracker_) berbasis web dengan arsitektur **Single-Page Application (SPA)** yang dibangun menggunakan **FastAPI**, **Vue 3**, **Tailwind CSS v4**, dan **PostgreSQL**. Dirancang untuk mengelola alur kerja harian secara dinamis tanpa _reload_ halaman, dilengkapi validasi data ketat, tampilan _Modern Minimal_, serta cakupan pengujian otomatis.

---

## Fitur Utama

### Manajemen Tugas & Alur Kerja

- **Operasi CRUD Lengkap:** Membuat, melihat, memperbarui, dan menghapus tugas dengan status `Todo`, `In Progress`, dan `Done`.
- **Pencatatan Waktu Selesai (`completed_at`):** Mencatat _timestamp_ penyelesaian secara otomatis saat status berubah menjadi `Done` dan meresetnya jika tugas dikembalikan ke `Todo` atau `In Progress`.
- **Deadline Opsional & Indikator Overdue:** Mendukung penetapan tanggal tenggat (`due_date`) dengan penanda otomatis **Overdue** pada tugas melewati batas waktu yang belum selesai, lengkap dengan filter cepat `Overdue`.
- **Side-Peek Detail Drawer:** Klik pada kartu tugas untuk membuka panel detail di sisi kanan layar guna membaca atau menyunting catatan panjang, status, dan deadline tanpa berpindah halaman.

### Tampilan & Navigasi SPA

- **List View & Kanban Board:** Beralih secara instan antara tampilan daftar vertikal dan papan Kanban 3 kolom yang mendukung _native drag-and-drop_ antar status.
- **Workspace Sidebar Responsif:** Navigasi terpadu untuk berpindah antara **Tugas Aktif** dan **Tong Sampah**, pintasan filter status, tombol _collapse_ di desktop/mobile, serta **Progress Bar** penyelesaian tugas secara _real-time_.
- **Live Search, Sorting, & Filter Reset:** Pencarian instan berdasarkan judul maupun deskripsi, pengurutan (_Terbaru_, _Terlama_, _Deadline Terdekat_, _Baru Selesai_), serta tombol **Reset** untuk membersihkan filter aktif.
- **Keyboard Shortcuts:** Mendukung `Ctrl + Enter` (`Cmd + Enter` di macOS) untuk menyimpan tugas/perubahan dengan cepat dan `Esc` untuk menutup _drawer_, modal konfirmasi, maupun menu mobile.

### Keamanan Data & Pengujian

- **30-Day Recycle Bin (Soft Delete):** Tugas yang dihapus dipindahkan ke **Tong Sampah** terlebih dahulu sehingga dapat dipulihkan (_Restore_), dihapus permanen satu per satu, dikosongkan sekaligus, atau dibersihkan otomatis (_auto-purge_) setelah melewati masa simpan 30 hari.
- **Automated API Testing (`pytest`):** Dilengkapi 10 skenario pengujian otomatis menggunakan `pytest` dan FastAPI `TestClient` di atas database SQLite _in-memory_ terisolasi.

---

## Teknologi yang Digunakan

- **Backend:** Python 3, FastAPI, SQLAlchemy ORM, Pydantic v2, Uvicorn
- **Database:** PostgreSQL
- **Frontend:** Vue 3 (Composition API `<script setup>`), Vite, Tailwind CSS v4, Axios
- **Testing:** Pytest, HTTPX

---

## Struktur Proyek

```text
task-tracker/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── tasks.py        # Endpoint REST API & logika Recycle Bin
│   │   ├── database.py         # Konfigurasi koneksi PostgreSQL via .env
│   │   ├── main.py             # Inisialisasi FastAPI, CORS, & tabel DB
│   │   ├── models.py           # Model SQLAlchemy (Task)
│   │   └── schemas.py          # Validasi request & response Pydantic
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_tasks.py       # Automated API test suite (10 test cases)
│   ├── .env.example            # Template konfigurasi environment backend
│   ├── pytest.ini              # Konfigurasi pythonpath untuk pytest
│   └── requirements.txt        # Daftar dependensi Python
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConfirmModal.vue
│   │   │   ├── KanbanBoard.vue
│   │   │   ├── SidebarNav.vue
│   │   │   ├── TaskDetailDrawer.vue
│   │   │   ├── TaskForm.vue
│   │   │   ├── TaskItem.vue
│   │   │   ├── ToastNotification.vue
│   │   │   └── TrashView.vue
│   │   ├── services/
│   │   │   └── taskService.js  # HTTP client Axios terpusat
│   │   ├── App.vue             # Root SPA state & layout
│   │   ├── main.js
│   │   └── style.css           # Konfigurasi Tailwind v4 & palet Modern Minimal
│   ├── .env.example            # Template konfigurasi environment frontend
│   └── package.json
├── README.md
└── TEST_CASES.md               # Dokumentasi skenario pengujian & payload Postman
```

---

## Panduan Instalasi & Menjalankan Aplikasi

### Prasyarat

- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL 14+

### 1. Konfigurasi Database PostgreSQL

Buat database kosong bernama `tasks_db` menggunakan salah satu cara berikut:

- **Via Terminal (`psql`):**
  ```bash
  psql -U postgres -c "CREATE DATABASE tasks_db;"
  ```

_(Tabel `tasks` beserta seluruh kolomnya akan dibuat secara otomatis oleh SQLAlchemy melalui `Base.metadata.create_all()` saat server backend pertama kali dijalankan.)_

### 2. Setup & Menjalankan Backend (FastAPI)

```bash
cd backend
python -m venv venv

# Aktifkan virtual environment:
# Windows (PowerShell):
.\venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

Salin file `.env.example` menjadi `.env` melalui terminal (berlaku untuk Windows PowerShell, macOS, maupun Linux):

```bash
cp .env.example .env
```

Buka file `.env` (misalnya via `notepad .env` di Windows atau `nano .env` di macOS/Linux), lalu sesuaikan `DB_PASSWORD` dengan password PostgreSQL lokal Anda:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password_postgres_anda
DB_NAME=tasks_db
```

Jalankan server pengembangan FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend berjalan di `http://127.0.0.1:8000` (dokumentasi interaktif Swagger UI dapat diakses di `http://127.0.0.1:8000/docs`).

### 3. Setup & Menjalankan Frontend (Vue 3)

Buka terminal baru, masuk ke folder `frontend`, lalu jalankan perintah berikut:

```bash
cd frontend
npm install
```

Salin `.env.example` menjadi `.env`

```bash
cp .env.example .env
```

Lalu sesuaikan alamat API backend:

```env
VITE_API_BASE_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
```

Jalankan server pengembangan Vite:

```bash
npm run dev
```

Aplikasi frontend berjalan di `http://localhost:5173`.

---

## Menjalankan Pengujian (`pytest` & Manual)

Untuk menjalankan seluruh _automated test_ endpoint API (menggunakan database SQLite _in-memory_ sehingga aman dan tidak mengubah data PostgreSQL), pastikan `venv` aktif lalu jalankan:

```bash
cd backend

# Aktifkan virtual environment jika belum aktif:
# Windows (PowerShell):
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pytest -v
```

Daftar lengkap skenario pengujian otomatis, payload JSON siap uji untuk Postman, serta pengujian fungsional antarmuka tercatat di [`TEST_CASES.md`](./TEST_CASES.md).

---

## Daftar Endpoint REST API

| Method   | Endpoint                | Deskripsi                                                         |
| :------- | :---------------------- | :---------------------------------------------------------------- |
| `GET`    | `/tasks`                | Mengambil seluruh daftar tugas aktif (`deleted_at IS NULL`)       |
| `POST`   | `/tasks`                | Membuat tugas baru (`title`, `description`, `status`, `due_date`) |
| `PUT`    | `/tasks/{id}`           | Memperbarui judul, deskripsi, status, atau deadline tugas         |
| `DELETE` | `/tasks/{id}`           | Memindahkan tugas ke tong sampah (_soft delete_)                  |
| `GET`    | `/tasks/trash`          | Mengambil daftar tugas di tong sampah beserta sisa hari retensi   |
| `POST`   | `/tasks/{id}/restore`   | Memulihkan tugas dari tong sampah ke daftar aktif                 |
| `DELETE` | `/tasks/{id}/permanent` | Menghapus satu tugas secara permanen dari database                |
| `DELETE` | `/tasks/trash/empty`    | Mengosongkan seluruh isi tong sampah secara permanen              |

---

## Keyboard Shortcuts

| Shortcut                       | Konteks                              | Fungsi                                                     |
| :----------------------------- | :----------------------------------- | :--------------------------------------------------------- |
| `Ctrl + Enter` / `Cmd + Enter` | Form Tugas Baru & Detail Drawer      | Menyimpan tugas baru atau perubahan detail secara langsung |
| `Esc`                          | Modal, Detail Drawer, Sidebar Mobile | Menutup lapisan overlay yang sedang aktif                  |
