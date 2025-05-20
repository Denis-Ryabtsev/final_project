from pydantic import BaseModel, Field


class NewsCreate(BaseModel):
    """
        Схема для создания новости

        Fields:
        - title: Заголовок новости.
        - description: Тело новости.
    """

    title: str = Field(min_length=4, max_length=40)
    description: str = Field(max_length=400)


class NewsRead(BaseModel):
    """
        Схема для получения новости

        Fields:
        - owner_id: Идентификатор пользователя, который выставил новость.
        - company_id: Идентификатор компании.
        - title: Заголовок новости.
        - description: Тело новости.
    """

    owner_id: int
    company_id: int
    title: str
    description: str

    model_config = {
        'from_attributes': True
    }