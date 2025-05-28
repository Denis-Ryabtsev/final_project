from datetime import date, time
from typing import Annotated, Optional
from pydantic import BaseModel, Field, constr, field_validator


class MeetingCreate(BaseModel):
    """
        Схема для создания встреч

        Fields:
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

    title: str = Field(min_length=4, max_length=40)
    description: str = Field(min_length=0, max_length=400)
    meeting_date: date
    meeting_time: time


class MeetingRead(BaseModel):
    """
        Схема для чтения встреч

        Fields:
        - organizer_id: Идентификатор организатора встречи.
        - company_id: Идентификатор компании.
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

    organizer_id: int
    company_id: int
    title: str
    description: str
    meeting_date: date
    meeting_time: time

    model_config = {
        'from_attributes': True
    }


StrippedStr = Annotated[str, constr(strip_whitespace=True)]

class MeetingChange(BaseModel):
    """
        Схема для изменения встреч

        Fields:
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

    title: Optional[StrippedStr] = None
    description: Optional[StrippedStr] = None
    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None

    @field_validator("meeting_date", "meeting_time", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class MeetingResponse(BaseModel):
    """
        Схема для возврата сообщения

        Fields:
        - message: Тело сообщения. Используется при успешном 
        добавлении пользователя на встречу
    """

    message: str