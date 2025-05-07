from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class Department(Base):
    """
        Модель отдела компании
    
        Fields:
        - id: Идентификатор отдела
        - name: Название отдела.
        - company_id: Идентификатор компании.
        - head_user_id: Руководитель отдела.
    """

    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    head_user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', use_alter=True, deferrable=True), nullable=False
    )

    __table_args__ = (
        Index("idx_department_company", "company_id"),
        Index("idx_department_head", "head_user_id"),
    )