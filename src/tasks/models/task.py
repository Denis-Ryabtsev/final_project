import datetime
from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base



if TYPE_CHECKING:
    from users.models import User
    from tasks.models.comment import Comment
    from company.models.company import Company
    from rating.models import Rating
    from calendars.models import Calendar

class TaskStatus(enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'


class Task(Base):
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

#     owner: Mapped['User'] = relationship(
#         back_populates='owner_task', foreign_keys=[owner_id]
#     )
#     target: Mapped['User'] = relationship(
#         back_populates='target_task', foreign_keys=[target_id]
#     )
#     company: Mapped['Company'] = relationship(
#         back_populates='task'
#     )
#     comment: Mapped[list['Comment']] = relationship(
#         back_populates='task', cascade='all, delete-orphan'
#     )
#     ratings: Mapped[list["Rating"]] = relationship(
#     back_populates="task",
#     cascade="all, delete-orphan"
# )

#     calendar_event: Mapped[Optional["Calendar"]] = relationship(
#     back_populates="task", uselist=False
# )

