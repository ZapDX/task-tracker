from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

RETENTION_DAYS = 30

def purge_expired_tasks(db: Session) -> None:
    """Menghapus permanen tugas di tong sampah yang sudah melewati 30 hari."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    db.query(models.Task).filter(
        models.Task.deleted_at.is_not(None),
        models.Task.deleted_at <= cutoff
    ).delete(synchronize_session=False)
    db.commit()

@router.get("", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    purge_expired_tasks(db)
    return (
        db.query(models.Task)
        .filter(models.Task.deleted_at.is_(None))
        .order_by(models.Task.created_at.desc(), models.Task.id.desc())
        .all()
    )

@router.get("/trash", response_model=List[schemas.TaskResponse])
def get_trashed_tasks(db: Session = Depends(get_db)):
    purge_expired_tasks(db)
    return (
        db.query(models.Task)
        .filter(models.Task.deleted_at.is_not(None))
        .order_by(models.Task.deleted_at.desc(), models.Task.id.desc())
        .all()
    )

@router.post("", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)):
    completed_time = (
        datetime.now(timezone.utc)
        if task_in.status == schemas.TaskStatus.DONE
        else None
    )
    new_task = models.Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status.value,
        due_date=task_in.due_date,
        completed_at=completed_time
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.delete("/trash/empty", status_code=status.HTTP_204_NO_CONTENT)
def empty_trash(db: Session = Depends(get_db)):
    """Menghapus permanen seluruh isi tong sampah."""
    db.query(models.Task).filter(
        models.Task.deleted_at.is_not(None)
    ).delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_in: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.deleted_at.is_(None))
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tugas dengan ID {task_id} tidak ditemukan"
        )

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"title", "status"} and value is None:
            continue
        if field == "status":
            new_status = value.value
            if new_status == schemas.TaskStatus.DONE.value:
                if task.status != schemas.TaskStatus.DONE.value or task.completed_at is None:
                    task.completed_at = datetime.now(timezone.utc)
            else:
                task.completed_at = None
            task.status = new_status
        elif field == "description" and value is None:
            task.description = ""
        else:
            setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_task(task_id: int, db: Session = Depends(get_db)):
    """Memindahkan tugas ke tong sampah (soft delete)."""
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.deleted_at.is_(None))
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tugas dengan ID {task_id} tidak ditemukan"
        )

    task.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{task_id}/restore", response_model=schemas.TaskResponse)
def restore_task(task_id: int, db: Session = Depends(get_db)):
    """Mengembalikan tugas dari tong sampah ke daftar aktif."""
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.deleted_at.is_not(None))
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tugas dengan ID {task_id} tidak ditemukan di tong sampah"
        )

    task.deleted_at = None
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanent_delete_task(task_id: int, db: Session = Depends(get_db)):
    """Menghapus permanen satu tugas dari tong sampah."""
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.deleted_at.is_not(None))
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tugas dengan ID {task_id} tidak ditemukan di tong sampah"
        )

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)