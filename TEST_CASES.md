# Test Cases — Simple Task / Project Tracker

Dokumen ini berisi skenario pengujian fungsional, validasi batas (_boundary & edge cases_), payload JSON siap pakai untuk pengujian API di Postman, serta pengujian antarmuka untuk **Simple Task / Project Tracker**.

---

## Bagian 1: Pengujian REST API & Database (Automated via `pytest`)

Seluruh skenario di bawah ini telah diotomatisasi di `backend/tests/test_tasks.py` dan dapat dijalankan dengan perintah `pytest -v` dari folder `backend/`.

| Kode          | Skenario Pengujian                        | Endpoint & Input                                                                                                                       | Hasil yang Diharapkan                                                                                                                                       |
| :------------ | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TC-API-01** | **Create Task Lengkap**                   | `POST /tasks` dengan `title`, `description`, `status`, dan `due_date` (`YYYY-MM-DD`).                                                  | Status `201 Created`; objek mengembalikan seluruh field sesuai input, `completed_at: null`, dan `deleted_at: null`.                                         |
| **TC-API-02** | **Create Task Minimal & Trimming**        | `POST /tasks` hanya dengan `{"title": "   Judul   "}`.                                                                                 | Status `201 Created`; spasi di ujung judul dipangkas otomatis, `description` default `""`, dan `status` default `"Todo"`.                                   |
| **TC-API-03** | **Validasi Input Gagal**                  | `POST /tasks` dengan judul kosong `""`, spasi saja `"   "`, judul > 255 karakter, status di luar Enum, atau format tanggal salah.      | Status `422 Unprocessable Entity`; tidak ada data korup masuk ke database.                                                                                  |
| **TC-API-04** | **Urutan Daftar Tugas Deterministik**     | `GET /tasks` setelah membuat beberapa tugas secara berurutan.                                                                          | Status `200 OK`; daftar terurut berdasarkan `created_at DESC, id DESC` (tugas terbaru selalu di posisi teratas meski dibuat di detik yang sama).            |
| **TC-API-05** | **Partial Update & Null Safety**          | `PUT /tasks/{id}` hanya mengirim `{"status": "In Progress"}`, mengirim `{"title": null}`, dan menghapus deadline `{"due_date": null}`. | Status `200 OK`; field lain tidak tertimpa, nilai `null` pada field wajib diabaikan aman, dan `due_date` dapat di-reset ke `null`.                          |
| **TC-API-06** | **Siklus Timestamp `completed_at`**       | Ubah status ke `"Done"`, edit judul saat `"Done"`, lalu kembalikan status ke `"In Progress"`.                                          | `completed_at` terisi otomatis saat `"Done"`, tetap terjaga saat judul diedit, dan kembali menjadi `null` saat status batal `"Done"`.                       |
| **TC-API-07** | **Soft Delete & Restore Recycle Bin**     | `DELETE /tasks/{id}` -> cek `GET /tasks` -> cek `GET /tasks/trash` -> `POST /tasks/{id}/restore`.                                      | `DELETE` mengembalikan `204 No Content`; tugas berpindah ke `/tasks/trash` dengan `days_remaining` (29–30 hari) dan kembali ke `/tasks` setelah di-restore. |
| **TC-API-08** | **Hapus Permanen & Empty Trash**          | `DELETE /tasks/{id}/permanent` dan `DELETE /tasks/trash/empty`.                                                                        | Status `204 No Content`; data terhapus permanen dari tabel PostgreSQL `tasks`.                                                                              |
| **TC-API-09** | **Auto-Purge 30 Hari**                    | Tugas di tong sampah dengan `deleted_at` > 30 hari lalu dipanggil `GET /tasks/trash`.                                                  | Tugas yang melewati batas retensi 30 hari otomatis dihapus permanen dari database.                                                                          |
| **TC-API-10** | **ID Tidak Ditemukan & Karakter Spesial** | Akses ID `99999` dan simpan string berisi karakter SQL/HTML (`'OR 1=1;-- <script>`).                                                   | ID tidak valid mengembalikan `404 Not Found`; karakter khusus tersimpan literal secara aman via ORM parameterization.                                       |

---

## Bagian 2: Panduan & Payload JSON Pengujian Manual (Postman)

Gunakan Base URL `http://127.0.0.1:8000` dan pilih **Body → raw → JSON** pada Postman untuk skenario yang membutuhkan request body.

### 1. Endpoint `POST /tasks` (Membuat Tugas Baru)

- **TC-API-01 — Create Task Lengkap** (`201 Created`)

```json
{
  "title": "Integrasi API & Frontend",
  "description": "Menghubungkan Vue 3 dengan FastAPI dan PostgreSQL",
  "status": "Todo",
  "due_date": "2026-12-01"
}
```

- **TC-API-01B — Create Task dengan Deadline Terlewat untuk Simulasi Overdue** (`201 Created`)

```json
{
  "title": "Setup Environment & Database",
  "description": "Konfigurasi PostgreSQL lokal dan kredensial .env",
  "status": "In Progress",
  "due_date": "2026-11-20"
}
```

- **TC-API-02 — Create Task Minimal & Auto-Trimming Spasi** (`201 Created`)

```json
{
  "title": "   Rapikan Dokumentasi README   "
}
```

- **TC-API-03A — Negative Test: Judul Kosong / Spasi Saja** (`422 Unprocessable Entity`)

```json
{
  "title": "     ",
  "status": "Todo"
}
```

- **TC-API-03B — Negative Test: Status di Luar Enum** (`422 Unprocessable Entity`)

```json
{
  "title": "Cek Validasi Status",
  "status": "Selesai"
}
```

- **TC-API-03C — Negative Test: Format Tanggal Salah** (`422 Unprocessable Entity`)

```json
{
  "title": "Cek Validasi Format Tanggal",
  "due_date": "01-12-2026"
}
```

- **TC-API-10 — Security Test: Karakter Spesial SQL/HTML** (`201 Created` — tersimpan literal aman)

```json
{
  "title": "Cek 100% _wildcard_ 'OR 1=1;-- <script>alert(1)</script>",
  "description": "Memastikan karakter khusus tersimpan literal secara aman"
}
```

### 2. Endpoint `PUT /tasks/{id}` (Pembaruan Tugas & Siklus `completed_at`)

_(Ganti `{id}` pada URL dengan ID tugas aktif yang valid, misalnya `http://127.0.0.1:8000/tasks/1`)_

- **TC-API-05A — Partial Update Status Saja** (`200 OK` — field lain tidak tertimpa)

```json
{
  "status": "In Progress"
}
```

- **TC-API-05B — Null Safety pada Field Wajib** (`200 OK` — nilai `null` diabaikan aman)

```json
{
  "title": null,
  "status": null
}
```

- **TC-API-05C — Reset / Hapus Deadline ke `null`** (`200 OK`)

```json
{
  "due_date": null
}
```

- **TC-API-06A — Tandai Tugas Selesai** (`200 OK` — `completed_at` terisi timestamp otomatis)

```json
{
  "status": "Done"
}
```

- **TC-API-06B — Edit Judul Saat Status Tetap `Done`** (`200 OK` — `completed_at` tetap mempertahankan waktu selesai awal)

```json
{
  "title": "Integrasi API & Frontend (Revisi Final)"
}
```

- **TC-API-06C — Kembalikan Status dari `Done`** (`200 OK` — `completed_at` kembali `null`)

```json
{
  "status": "In Progress"
}
```

- **TC-API-10B — Negative Test: Update ID Tidak Ditemukan** (`PUT /tasks/99999` → `404 Not Found`)

```json
{
  "status": "Done"
}
```

### 3. Endpoint Tanpa Request Body (`GET`, `DELETE`, & `POST /restore`)

Pastikan tab **Body** di Postman diset ke **none** untuk pengujian berikut:

| Kode           | Method & URL                                        | Hasil yang Diharapkan                                                                         |
| :------------- | :-------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| **TC-API-04**  | `GET http://127.0.0.1:8000/tasks`                   | Status `200 OK`; mengembalikan array seluruh tugas aktif terurut dari terbaru.                |
| **TC-API-07A** | `DELETE http://127.0.0.1:8000/tasks/{id}`           | Status `204 No Content`; tugas dipindahkan ke tong sampah (`deleted_at` terisi).              |
| **TC-API-07B** | `GET http://127.0.0.1:8000/tasks/trash`             | Status `200 OK`; mengembalikan daftar tugas terhapus lengkap dengan `days_remaining` (29–30). |
| **TC-API-07C** | `POST http://127.0.0.1:8000/tasks/{id}/restore`     | Status `200 OK`; tugas dipulihkan ke daftar aktif (`deleted_at: null`).                       |
| **TC-API-08A** | `DELETE http://127.0.0.1:8000/tasks/{id}/permanent` | Status `204 No Content`; menghapus permanen 1 tugas dari tong sampah.                         |
| **TC-API-08B** | `DELETE http://127.0.0.1:8000/tasks/trash/empty`    | Status `204 No Content`; mengosongkan seluruh isi tong sampah secara permanen.                |

---

## Bagian 3: Pengujian Antarmuka, Interaksi UX, & Edge Cases (Frontend Vue 3)

| Kode         | Skenario Pengujian                                | Langkah Eksekusi                                                                                                                                 | Hasil yang Diharapkan                                                                                                                                                                                                 |
| :----------- | :------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TC-UI-01** | **Dynamic Create & Form Reset**                   | Isi judul, deskripsi, status, dan deadline opsional lalu klik **+ Tambah Tugas**.                                                                | Tugas langsung muncul di daftar tanpa reload halaman, seluruh input form kembali kosong/default, dan notifikasi toast muncul.                                                                                         |
| **TC-UI-02** | **Indikator Deadline (`Hari ini` vs. `Overdue`)** | Buat tugas berstatus `Todo` dengan tanggal hari ini dan tugas lain dengan tanggal kemarin, lalu ubah tugas kemarin menjadi `Done`.               | Tugas hari ini menampilkan badge kuning **Hari ini** di detail drawer; tugas kemarin menampilkan badge merah **Overdue** selama belum `Done`, dan badge otomatis hilang saat ditandai `Done`.                         |
| **TC-UI-03** | **Filter Pill `Overdue` & Tombol `Reset`**        | Klik pill filter **Overdue** di toolbar, ketik kata kunci di kolom pencarian, lalu klik tombol **Reset**.                                        | Pill `Overdue` hanya menampilkan tugas telat yang belum `Done` dengan counter akurat; tombol **Reset** muncul otomatis saat filter/pencarian aktif dan mengembalikan tampilan ke `All` serta mengosongkan kolom cari. |
| **TC-UI-04** | **Side-Peek Detail Drawer & Reset Deadline**      | Klik kartu tugas pada List atau Board, edit deskripsi panjang, klik **Reset** di samping input tanggal deadline, lalu klik **Simpan Perubahan**. | Panel detail meluncur dari kanan tanpa pindah halaman; tombol simpan hanya aktif jika ada perubahan; setelah disimpan, deadline terhapus (`null`) dan kartu langsung sinkron.                                         |
| **TC-UI-05** | **Hapus Tugas Saat Drawer Terbuka**               | Buka Side-Peek Detail Drawer suatu tugas -> klik tombol **Hapus** di header drawer -> klik konfirmasi pada modal.                                | Modal konfirmasi muncul di atas drawer; setelah dikonfirmasi, tugas pindah ke Tong Sampah dan panel detail otomatis tertutup bersih tanpa menyisakan state kosong.                                                    |
| **TC-UI-06** | **Keyboard Shortcuts (`Ctrl + Enter` & `Esc`)**   | Tekan `Ctrl + Enter` saat mengetik di form tugas baru dan di dalam Side-Peek Drawer; uji juga menekan `Esc` saat modal terbuka di atas drawer.   | `Ctrl + Enter` langsung menyimpan data (dan tidak mengirim request ganda jika belum ada perubahan di drawer); tombol `Esc` menutup lapisan paling atas secara berurutan (Modal -> Drawer -> Sidebar Mobile).          |
| **TC-UI-07** | **Toggle List vs. Kanban Board & Drag-and-Drop**  | Aktifkan filter `Overdue` di mode **List**, pindah ke mode **Board**, seret kartu dari `Todo` ke `Done`, lalu tekan `F5`.                        | Perpindahan ke `Board` otomatis me-reset filter ke `All` agar ketiga kolom tampil utuh; kartu yang di-drag berpindah status, mencatat waktu `Selesai`, dan tetap bertahan setelah browser di-refresh.                 |
| **TC-UI-08** | **Live Search & Multi-Criteria Sorting**          | Cari kata kunci yang hanya ada di deskripsi, lalu uji urutan `Terbaru`, `Terlama`, `Deadline Terdekat`, dan `Baru Selesai`.                      | Pencarian mencocokkan judul maupun deskripsi secara instan; pada opsi `Deadline Terdekat`, tugas dengan tenggat paling awal berada di atas dan tugas tanpa deadline diletakkan di bagian bawah.                       |
| **TC-UI-09** | **Workspace Sidebar & Progress Bar**              | Uji buka-tutup sidebar di desktop dan mobile, scroll daftar tugas yang panjang ke bawah, serta pantau bar persentase di bagian atas sidebar.     | Drawer mobile memiliki latar solid tanpa bertumpuk dengan konten belakang; sidebar desktop tetap diam (`sticky`) saat halaman di-scroll dan bisa dilipat; persentase selesai terhitung akurat secara _real-time_.     |
| **TC-UI-10** | **Alur Tong Sampah, Restore, & Empty Trash**      | Hapus tugas -> buka menu **Tong Sampah** di sidebar -> uji tombol **Pulihkan** pada satu tugas dan **Kosongkan Tong Sampah** untuk sisanya.      | Counter badge Tong Sampah langsung bertambah/berkurang; sisa hari retensi tampil; tugas yang dipulihkan kembali ke daftar aktif; dan aksi kosongkan tong sampah membersihkan seluruh daftar terhapus.                 |
| **TC-UI-11** | **Penanganan Error Koneksi Backend**              | Matikan server FastAPI sementara -> lakukan refresh halaman atau coba ubah status tugas -> nyalakan server kembali dan klik **Coba Lagi**.       | Aplikasi tidak _crash_ (layar putih); muncul banner peringatan koneksi atau toast error yang jelas, dan data kembali dimuat normal saat tombol **Coba Lagi** diklik.                                                  |
