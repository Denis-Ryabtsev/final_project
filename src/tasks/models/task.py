import datetime
import enum

from sqlalchemy import String, Enum, Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class TaskStatus(enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'


class Task(Base):
    """
        Модель задачи
    
        Fields:
        - id: Идентификатор задачи
        - company_id: Идентификатор компании.
        - owner_id: Идентификатор пользователя, установившего задачу.
        - target_id: Идентификатор исполнителя задачи.
        - start_date: Начало задачи.
        - end_date: Окончание задачи.
        - title: Название задачи.
        - description: Описание задачи.
        - status: Статус задачи.
    """

    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    start_date: Mapped[datetime.date] = mapped_column(nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(400), nullable=False)
    description: Mapped[str] = mapped_column(String(1024))
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.todo)

    #   настройка индексов
    __table_args__ = (
        Index('idx_company_id', 'company_id'),
        Index('idx_owner_id', 'owner_id'),
        Index('idx_target_id', 'target_id'),
        Index('idx_status', 'status'),
        Index('idx_start_end_date', 'start_date', 'end_date'),
    )