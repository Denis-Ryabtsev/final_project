from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base



class News(Base):
    """
        Модель новостей компании

        Fields:
        - id: Идентификатор новости
        - owner_id: Идентификатор пользователя, который выставил новость.
        - company_id: Идентификатор компании.
        - title: Заголовок новости.
        - description: Тело новости.
    """

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

    #   настройка индексов
    __table_args__ = (
        Index("idx_news_owner_id", "owner_id"),
        Index("idx_news_company_id", "company_id"),
    )