import datetime
from typing import Optional
import enum

from sqlalchemy import Enum, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class CalendarStatus(enum.Enum):
    task = 'task'
    meeting = 'meeting'


class Calendar(Base):
    """
        Модель календаря пользователя
    
        Fields:
        - id: Идентификатор записи события
        - user_id: Идентификатор пользователя.
        - event_date: Дата события.
        - event_time: Время события.
        - title: Заголовок события
        - type_event: Тип события
        - task_id: Идентификатор задачи
        - meeting_id: Идентификатор встречи
    """

    __tablename__ = 'calendar'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(nullable=False)
    event_time: Mapped[datetime.time] = mapped_column(nullable=True)
    
    title: Mapped[str] = mapped_column(nullable=False)
    type_event: Mapped[CalendarStatus] = mapped_column(Enum(CalendarStatus))

    task_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("task.id", ondelete="CASCADE"), nullable=True
    )
    meeting_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("meeting.id", ondelete="CASCADE"), nullable=True
    )

    #   настройка ограничений и индексов
    __table_args__ = (
        UniqueConstraint("user_id", "event_date", "event_time", name="uix_user_datetime"),
        Index("idx_calendar_user", "user_id"),
        Index("idx_calendar_date", "event_date"),
        Index("idx_calendar_task", "task_id"),
        Index("idx_calendar_meeting", "meeting_id"),
    )