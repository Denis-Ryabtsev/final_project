from datetime import date, time
from typing import Optional
from pydantic import BaseModel, field_validator


class MeetingCreate(BaseModel):
    """
        Схема для создания встреч

        Fields:
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

    title: str
    description: str
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


class MeetingChange(BaseModel):
    """
        Схема для изменения встреч

        Fields:
        - title: Заголовок встречи.
        - description: Описание встречи.
        - meeting_date: Дата встречи.
        - meeting_time: Время встречи.
    """

    title: Optional[str] = None
    description: Optional[str] = None

    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None

    @field_validator('meeting_date', mode='before')
    @classmethod
    def parse_optional_date(cls, v):
        if v == '':
            return None
        return v

    @field_validator('meeting_time', mode='before')
    @classmethod
    def parse_optional_time(cls, v):
        if v == '':
            return None
        return v


class MeetingResponse(BaseModel):
    """
        Схема для возврата сообщения

        Fields:
        - message: Тело сообщения
    """

    message: str