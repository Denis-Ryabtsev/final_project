from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Enum, Index, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base


if TYPE_CHECKING:
    from users.models import User
    from company.models.department import Department

class Company(Base):
    __tablename__ = 'company'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    company_code: Mapped[str] = mapped_column(String(4), nullable=False)
    admin_code: Mapped[str] = mapped_column(String(6), nullable=False)

    users: Mapped[list['User']] = relationship(
        back_populates='company', cascade="all, delete-orphan"
    )
    departments: Mapped[list['Department']] = relationship(
        back_populates='company', cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_code', 'company_code'),
    )
