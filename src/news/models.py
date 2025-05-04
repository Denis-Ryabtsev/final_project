from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base
from users.models import User
from company.models.company import Company

if TYPE_CHECKING:
    from company.models.company import Company


class News(Base):
    __tablename__ = 'news'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)

    authors: Mapped['User'] = relationship(back_populates='news')
    company: Mapped['Company'] = relationship(back_populates='news')