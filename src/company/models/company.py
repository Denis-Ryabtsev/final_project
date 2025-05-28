from sqlalchemy import String, Index
from sqlalchemy.orm import mapped_column, Mapped

from database import Base

    
class Company(Base):
    """
        Модель компании
    
        Fields:
        - id: Идентификатор компании
        - name: Название компании.
        - description: Описание команды.
        - company_code: Код приглашения команды.
        - admin_code: Админ код для назначение роли админа.
    """

    __tablename__ = 'company'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    company_code: Mapped[str] = mapped_column(String(4), nullable=False)
    admin_code: Mapped[str] = mapped_column(String(6), nullable=False)

    __table_args__ = (
        Index('idx_code', 'company_code'),
        Index('idx_admin_code', 'admin_code'),
    )
