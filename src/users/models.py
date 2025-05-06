from typing import TYPE_CHECKING, Optional
import enum

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base
from tasks.models.comment import Comment
from calendars.models import Calendar

if TYPE_CHECKING:
    from company.models.company import Company
    from company.models.department import Department
    from news.models import News
    from tasks.models.task import Task
    # from tasks.models.comment import Comment
    from rating.models import Rating
    
    from meeting.models import Meeting
    # from calendars.models import Calendar
    
class RoleType(enum.Enum):
    employee = 'employee'
    manager = 'manager'
    admin = 'admin'


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(length=40), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=40), nullable=False)
    company_role: Mapped[RoleType] = mapped_column(
        Enum(RoleType), default=RoleType.employee ,nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='SET NULL'), nullable=True
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('department.id', ondelete='SET NULL'), nullable=True
    )
    email: Mapped[str] = mapped_column(String(length=30), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)



#     company: Mapped['Company'] = relationship(
#         back_populates='users', passive_deletes=True
#     )
#     department: Mapped[Optional['Department']] = relationship(
#         back_populates='users', passive_deletes=True, foreign_keys=[department_id]
#     )
#     news: Mapped[list['News']] = relationship(
#         back_populates='authors', cascade="all, delete-orphan"
#     )
#     owner_task: Mapped[list['Task']] = relationship(
#         back_populates='owner', cascade="all, delete-orphan", foreign_keys='Task.owner_id'
#     )
#     target_task: Mapped[list['Task']] = relationship(
#         back_populates='target', cascade="all, delete-orphan", foreign_keys='Task.target_id'
#     )
#     comments: Mapped[list['Comment']] = relationship(
#         back_populates='user', cascade="all, delete-orphan", lazy="selectin", foreign_keys="Comment.author_id"
#     )

#     received_ratings: Mapped[list["Rating"]] = relationship(
#         back_populates="employee",
#         foreign_keys="Rating.owner_id",
#         cascade="all, delete-orphan"
#     )

#     # Все оценки, которые выставил этот пользователь
#     given_ratings: Mapped[list["Rating"]] = relationship(
#         back_populates="evaluator",
#         foreign_keys="Rating.head_id",
#         cascade="all, delete-orphan"
#     )

    

#     organized_meetings: Mapped[list["Meeting"]] = relationship(
#     back_populates="organizer", cascade="all, delete-orphan"
# )
#     calendar_events: Mapped[list["Calendar"]] = relationship(
#         back_populates="user", cascade="all, delete-orphan"
#         )
    

    __table_args__ = (
        Index('idx_email', 'email'),
    )