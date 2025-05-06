from datetime import date, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


if TYPE_CHECKING:
    from users.models import User
    from tasks.models.comment import Comment
    from company.models.company import Company
    from rating.models import Rating
    from calendars.models import Calendar


class Meeting(Base):
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("company.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    meeting_date: Mapped[date] = mapped_column(nullable=False)
    meeting_time: Mapped[time] = mapped_column(nullable=False)

    # # ORM-связи
    # organizer: Mapped["User"] = relationship(back_populates="organized_meetings")
    # company: Mapped["Company"] = relationship(back_populates="meetings")

    # calendar_event: Mapped[list["Calendar"]] = relationship(
    #     back_populates="meeting", cascade="all, delete-orphan"
    # )
