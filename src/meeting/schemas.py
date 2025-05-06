from datetime import date, time
from typing import Optional
from pydantic import BaseModel


class MeetingCreate(BaseModel):
    title: str
    description: str

    meeting_date: date
    meeting_time: time


class MeetingRead(BaseModel):
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
    title: Optional[str] = None
    description: Optional[str] = None

    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None


class MeetingResponse(BaseModel):
    message: str