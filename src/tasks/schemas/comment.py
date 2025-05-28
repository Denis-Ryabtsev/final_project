from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """
        Схема для создания комментария

        Fields:
        - description: Тело комментария.
    """

    description: str = Field(max_length=400)


class CommentRead(BaseModel):
    """
        Схема для получения информации о комментарии

        Fields:
        - author_id: Идентификатор пользователя.
        - task_id: Идентификатор задачи.
        - description: Тело комментария.
    """

    author_id: int
    task_id: int
    description: str

    model_config = {
        'from_attributes': True
    }