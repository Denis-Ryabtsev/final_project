import datetime
from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base



if TYPE_CHECKING:
    from users.models import User
    from tasks.models.comment import Comment
    from company.models.company import Company
    from rating.models import Rating
    from tasks.models.task import Task
    from meeting.models import Meeting

class CalendarStatus(enum.Enum):
    task = 'task'
    meeting = 'meeting'


class Calendar(Base):
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

    
    __table_args__ = (
        UniqueConstraint("user_id", "event_date", "event_time", name="uix_user_datetime"),
    )

    # # Relationships
    # user = relationship("User", back_populates="calendar_events", )
    # task = relationship("Task", back_populates="calendar_event", lazy="selectin")
    # meeting = relationship("Meeting", back_populates="calendar_event", lazy="selectin")