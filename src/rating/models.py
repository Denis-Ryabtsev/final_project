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
    from tasks.models.task import Task
    from tasks.models.task import Task


class Rating(Base):
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

    employee: Mapped["User"] = relationship(
    foreign_keys=[owner_id],
    back_populates="received_ratings"
    )

    evaluator: Mapped["User"] = relationship(
        foreign_keys=[head_id],
        back_populates="given_ratings"
    )
    task: Mapped["Task"] = relationship(back_populates="ratings")