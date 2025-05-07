import datetime

from sqlalchemy import Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class Rating(Base):
    """
        Модель оценок задач
    
        Fields:
        - id: Идентификатор оценки
        - task_id: Идентификатор задачи.
        - owner_id: Исполнитель задачи.
        - head_id: Оценщик задачи.
        - score_date: Оценка дедлайна.
        - score_quality: Оценка качества.
        - score_complete: Оценка полноты выполнения.
        - created_at: Дата создания оценки.
    """

    __tablename__ = 'rating'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    head_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    score_date: Mapped[int] = mapped_column(nullable=False)
    score_quality: Mapped[int] = mapped_column(nullable=False)
    score_complete: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime.date] = mapped_column(default=datetime.date.today)

    #   настройка индексов
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_owner_id', 'owner_id'),
        Index('idx_head_id', 'head_id'),
        Index('idx_created_at', 'created_at'),
    )