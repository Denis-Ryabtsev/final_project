import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """
        Схема для создания оценок

        Fields:
        - score_date: Оценка дедлайна.
        - score_quality: Оценка качества.
        - score_complete: Оценка полноты выполнения.
    """

    score_date: int = Field(ge=1, lt=6)
    score_quality: int = Field(ge=1, lt=6)
    score_complete: int = Field(ge=1, lt=6)


class RatingRead(BaseModel):
    """
        Схема для получения оценки

        Fields:
        - task_id: Идентификатор задачи.
        - owner_id: Исполнитель задачи.
        - head_id: Оценщик задачи.
        - score_date: Оценка дедлайна.
        - score_quality: Оценка качества.
        - score_complete: Оценка полноты выполнения.
    """

    task_id: int
    owner_id: int
    head_id: int
    score_date: int
    score_quality: int
    score_complete: int

    model_config = {
        'from_attributes': True
    }


class RatingReadUser(BaseModel):
    """
        Схема для получения оценки пользователем

        Fields:
        - task_id: Идентификатор задачи.
        - head_id: Оценщик задачи.
        - score_date: Оценка дедлайна.
        - score_quality: Оценка качества.
        - score_complete: Оценка полноты выполнения.
        - created_at: Дата создания оценки.
    """

    task_id: int
    head_id: int
    score_date: int
    score_quality: int
    score_complete: int
    created_at: datetime.date

    model_config = {
        'from_attributes': True
    }


class AvgRatingRead(BaseModel):
    """
        Схема для получения средних значений оценок

        Fields:
        - avg_date: Средняя оценка дедлайна.
        - avg_quality: Средняя оценка качества.
        - avg_complete: Средняя оценка полноты выполнения.
    """

    avg_date: Optional[float] = None
    avg_quality: Optional[float] = None
    avg_complete: Optional[float] = None

    model_config = {
        'from_attributes': True
    }