import datetime
from typing import Optional
from pydantic import BaseModel

from tasks.models.task import TaskStatus


class TaskRead(BaseModel):
    owner_id: int
    company_id: int
    target_id: int
    start_date: datetime.date
    end_date: datetime.date
    title: str
    description: str
    status: TaskStatus

    model_config = {
        'from_attributes': True
    }


class TaskCreate(BaseModel):
    target_id: int
    start_date: datetime.date
    end_date: datetime.date
    title: str
    description: str


class TaskChange(BaseModel):
    company_id: Optional[int] = None
    target_id: Optional[int] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskChangeRole(BaseModel):
    status: TaskStatus