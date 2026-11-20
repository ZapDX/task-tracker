from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

class TaskStatus(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Judul tugas tidak boleh kosong atau hanya berisi spasi")
        return v.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Judul tugas tidak boleh kosong atau hanya berisi spasi")
        return v.strip() if v is not None else v

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[date] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @computed_field
    @property
    def days_remaining(self) -> Optional[int]:
        if self.deleted_at is None:
            return None
        deleted_utc = (
            self.deleted_at
            if self.deleted_at.tzinfo is not None
            else self.deleted_at.replace(tzinfo=timezone.utc)
        )
        expiry_date = deleted_utc + timedelta(days=30)
        remaining = (expiry_date - datetime.now(timezone.utc)).days
        return max(0, remaining)

    model_config = ConfigDict(from_attributes=True)