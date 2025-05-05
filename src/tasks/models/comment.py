import datetime
from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base

from company.models.company import Company

if TYPE_CHECKING:
    from users.models import User
    from tasks.models.task import Task


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey('task.id', ondelete='CASCADE'), nullable=False
    )
    description: Mapped[str] = mapped_column(String(1024), nullable=False)

    
    user: Mapped['User'] = relationship(back_populates='comments')
    task: Mapped['Task'] = relationship(
        back_populates='comment'
    )