from datetime import date, time
from typing import Optional

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Meeting(Base):
    """
        Модель встреч компании
    
        Fields:
        - id: Идентификатор встречи
        - organizer_id: Идентификатор организатора встречи.
        - company_id: Идентификатор компании.
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

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

    #   настройка индексов
    __table_args__ = (
        Index('idx_meeting_company', 'company_id'),
        Index('idx_meeting_organizer', 'organizer_id'),
        Index('idx_meeting_date_time', 'meeting_date', 'meeting_time'),
    )