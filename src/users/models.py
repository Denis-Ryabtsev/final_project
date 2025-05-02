import enum
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, String, Enum, Index
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class RoleType(enum.Enum):
    employee = 'employee'
    manager = 'manager'
    admin = 'admin'


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(length=160), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=160), nullable=False)
    role: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index('idx_email', 'email'),
    )