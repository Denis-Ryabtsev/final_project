from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class Comment(Base):
    """
        Модель комментариев к задачам
    
        Fields:
        - id: Идентификатор комментария
        - author_id: Идентификатор пользователя.
        - task_id: Идентификатор задачи.
        - description: Тело комментария.
    """

    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey('task.id', ondelete='CASCADE'), nullable=False
    )
    description: Mapped[str] = mapped_column(String(1024), nullable=False)

    #   настройка индексов
    __table_args__ = (
        Index('idx_author_id', 'author_id'),
        Index('idx_task_id', 'task_id'),
    )