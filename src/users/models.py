from typing import Optional
import enum

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Enum, Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base

    
class RoleType(enum.Enum):
    employee = 'employee'
    manager = 'manager'
    admin = 'admin'


class User(SQLAlchemyBaseUserTable, Base):
    """
        Модель пользователя системы
    
        Fields:
        - id: Идентификатор пользователя
        - first_name: Имя пользователя.
        - last_name: Фамилия пользователя.
        - company_role: Роль в компании.
        - company_id: Идентификатор компании.
        - department_id: Идентификатор отдела.
        - email: Почта пользователя.
        - hashed_password: Хеш пароля от учетной записи.
        - is_active: Флаг активности пользователя.
        - is_superuser: Флаг суперпользователя.
        - is_verified: Флаг подтверждения учетной записи.
    """

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

    #   настройка индексов
    __table_args__ = (
        Index('idx_email', 'email'),
    )