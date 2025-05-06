import datetime
from typing import Optional
from pydantic import BaseModel


class RatingCreate(BaseModel):
    score_date: int
    score_quality: int
    score_complete: int


class RatingRead(BaseModel):
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
    avg_date: Optional[float] = None
    avg_quality: Optional[float] = None
    avg_complete: Optional[float] = None

    model_config = {
        'from_attributes': True
    }