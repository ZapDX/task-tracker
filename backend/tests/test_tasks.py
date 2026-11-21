from datetime import date, datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Membuat skema tabel bersih sebelum setiap test dan membersihkannya setelah selesai."""
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_task_full():
    payload = {
        "title": "Integrasi API & Frontend",
        "description": "Menghubungkan Vue 3 dengan FastAPI",
        "status": "Todo",
        "due_date": "2026-12-01",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Integrasi API & Frontend"
    assert data["description"] == "Menghubungkan Vue 3 dengan FastAPI"
    assert data["status"] == "Todo"
    assert data["due_date"] == "2026-12-01"
    assert data["completed_at"] is None
    assert data["deleted_at"] is None


def test_create_task_minimal_defaults_and_trimming():
    response = client.post("/tasks", json={"title": "   Rapikan Dokumentasi   "})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Rapikan Dokumentasi"
    assert data["description"] == ""
    assert data["status"] == "Todo"
    assert data["due_date"] is None


def test_create_task_validation_errors():
    invalid_payloads = [
        {"title": "", "status": "Todo"},
        {"title": "     ", "status": "Todo"},
        {"title": "x" * 256, "status": "Todo"},
        {"title": "Valid Title", "status": "Selesai"},
        {"title": "Valid Title", "due_date": "31-12-2026"},
    ]
    for payload in invalid_payloads:
        res = client.post("/tasks", json=payload)
        assert res.status_code == 422


def test_get_tasks_ordering():
    client.post("/tasks", json={"title": "Tugas Pertama"})
    client.post("/tasks", json={"title": "Tugas Kedua"})

    res = client.get("/tasks")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert items[0]["title"] == "Tugas Kedua"
    assert items[1]["title"] == "Tugas Pertama"


def test_partial_update_null_safety_and_clear_due_date():
    created = client.post(
        "/tasks",
        json={
            "title": "Judul Awal",
            "description": "Deskripsi Awal",
            "status": "Todo",
            "due_date": "2026-12-15",
        },
    ).json()
    task_id = created["id"]

    # Partial update status saja tidak menimpa field lain
    res_status = client.put(f"/tasks/{task_id}", json={"status": "In Progress"})
    assert res_status.status_code == 200
    assert res_status.json()["title"] == "Judul Awal"
    assert res_status.json()["due_date"] == "2026-12-15"

    # Payload null pada field wajib diabaikan dengan aman (tidak 500)
    res_null = client.put(f"/tasks/{task_id}", json={"title": None, "status": None})
    assert res_null.status_code == 200
    assert res_null.json()["title"] == "Judul Awal"
    assert res_null.json()["status"] == "In Progress"

    # Menghapus deadline dengan due_date: null
    res_clear_due = client.put(f"/tasks/{task_id}", json={"due_date": None})
    assert res_clear_due.status_code == 200
    assert res_clear_due.json()["due_date"] is None


def test_completed_at_timestamp_lifecycle():
    # 1. Buat langsung berstatus Done -> completed_at otomatis terisi
    done_task = client.post(
        "/tasks", json={"title": "Langsung Selesai", "status": "Done"}
    ).json()
    assert done_task["completed_at"] is not None

    # 2. Buat Todo -> ubah ke Done -> edit judul -> revert ke Todo
    task = client.post("/tasks", json={"title": "Bertahap", "status": "Todo"}).json()
    assert task["completed_at"] is None

    updated_done = client.put(
        f"/tasks/{task['id']}", json={"status": "Done"}
    ).json()
    first_completed_at = updated_done["completed_at"]
    assert first_completed_at is not None

    # Edit judul saat status tetap Done -> mempertahankan timestamp selesai awal
    edited_title = client.put(
        f"/tasks/{task['id']}", json={"title": "Bertahap (Revisi)"}
    ).json()
    assert edited_title["completed_at"] == first_completed_at

    # Kembalikan ke In Progress -> completed_at di-reset menjadi None
    reverted = client.put(
        f"/tasks/{task['id']}", json={"status": "In Progress"}
    ).json()
    assert reverted["completed_at"] is None


def test_soft_delete_recycle_bin_and_restore():
    created = client.post("/tasks", json={"title": "Tugas Sementara"}).json()
    task_id = created["id"]

    # Soft delete
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    # Hilang dari daftar aktif & tidak bisa di-update langsung
    assert client.get("/tasks").json() == []
    assert client.put(f"/tasks/{task_id}", json={"status": "Done"}).status_code == 404

    # Muncul di tong sampah dengan sisa hari 29-30 hari
    trash_items = client.get("/tasks/trash").json()
    assert len(trash_items) == 1
    assert trash_items[0]["id"] == task_id
    assert trash_items[0]["days_remaining"] in (29, 30)

    # Restore dari tong sampah
    restore_res = client.post(f"/tasks/{task_id}/restore")
    assert restore_res.status_code == 200
    assert restore_res.json()["deleted_at"] is None
    assert client.get("/tasks/trash").json() == []
    assert len(client.get("/tasks").json()) == 1


def test_permanent_delete_and_empty_trash():
    t1 = client.post("/tasks", json={"title": "Item 1"}).json()["id"]
    t2 = client.post("/tasks", json={"title": "Item 2"}).json()["id"]
    t3 = client.post("/tasks", json={"title": "Item 3"}).json()["id"]

    client.delete(f"/tasks/{t1}")
    client.delete(f"/tasks/{t2}")
    client.delete(f"/tasks/{t3}")

    # Hapus permanen satu item
    res_perm = client.delete(f"/tasks/{t1}/permanent")
    assert res_perm.status_code == 204
    assert len(client.get("/tasks/trash").json()) == 2

    # Kosongkan seluruh tong sampah
    res_empty = client.delete("/tasks/trash/empty")
    assert res_empty.status_code == 204
    assert client.get("/tasks/trash").json() == []


def test_auto_purge_tasks_older_than_30_days():
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    expired_task = models.Task(
        title="Kadaluarsa 31 Hari",
        status="Todo",
        deleted_at=now - timedelta(days=31),
    )
    active_trash_task = models.Task(
        title="Baru Dihapus 5 Hari",
        status="Todo",
        deleted_at=now - timedelta(days=5),
    )
    db.add_all([expired_task, active_trash_task])
    db.commit()
    db.close()

    trash_items = client.get("/tasks/trash").json()
    assert len(trash_items) == 1
    assert trash_items[0]["title"] == "Baru Dihapus 5 Hari"
    assert trash_items[0]["days_remaining"] in (24, 25)


def test_not_found_and_special_characters_safety():
    assert client.put("/tasks/99999", json={"status": "Done"}).status_code == 404
    assert client.delete("/tasks/99999").status_code == 404
    assert client.post("/tasks/99999/restore").status_code == 404

    special_title = "Cek 100% _wildcard_ 'OR 1=1;-- <script>alert(1)</script>"
    res = client.post("/tasks", json={"title": special_title})
    assert res.status_code == 201
    assert res.json()["title"] == special_title