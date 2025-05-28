import datetime
from typing import Optional

from pydantic import BaseModel, Field

from tasks.models.task import TaskStatus


class TaskRead(BaseModel):
    """
        Схема для получения данных задачи

        Fields:
        - owner_id: Идентификатор пользователя, установившего задачу.
        - company_id: Идентификатор компании.
        - target_id: Идентификатор исполнителя задачи.
        - start_date: Начало задачи.
        - end_date: Окончание задачи.
        - title: Название задачи.
        - description: Описание задачи.
        - status: Статус задачи.
    """

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
    """
        Схема для создания новой задачи

        Fields:
        - target_id: Идентификатор исполнителя задачи.
        - start_date: Начало задачи.
        - end_date: Окончание задачи.
        - title: Название задачи.
        - description: Описание задачи.
    """

    target_id: int
    start_date: datetime.date
    end_date: datetime.date
    title: str = Field(min_length=4, max_length=40)
    description: str = Field(max_length=400)


class TaskChange(BaseModel):
    """
        Схема для изменения данных задачи

        Fields:
        - company_id: Идентификатор компании.
        - target_id: Идентификатор исполнителя задачи.
        - start_date: Начало задачи.
        - end_date: Окончание задачи.
        - title: Название задачи.
        - description: Описание задачи.
        - status: Статус задачи.
    """

    company_id: Optional[int] = None
    target_id: Optional[int] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    title: Optional[str] = Field(None, min_length=4, max_length=40)
    description: Optional[str] = Field(None, max_length=400)
    status: Optional[TaskStatus] = None


class TaskChangeRole(BaseModel):
    """
        Схема для изменения статуса задачи

        Fields:
        - status: Статус задачи.
    """

    status: TaskStatus
