from typing import TYPE_CHECKING
from sqlalchemy import Boolean, String, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database import Base


if TYPE_CHECKING:
    from users.models import User
    from company.models.company import Company

class Department(Base):
    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    head_user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', use_alter=True, deferrable=True), nullable=False
    )

    users: Mapped[list['User']] = relationship(
        back_populates='department', passive_deletes=True, foreign_keys='User.department_id'
    )
    company: Mapped['Company'] = relationship(back_populates='departments')
    head_user: Mapped['User'] = relationship(foreign_keys=[head_user_id], lazy='selectin')