from datetime import date, time
from typing import Optional
from pydantic import BaseModel
from calendars.models import CalendarStatus

class CalendarRead(BaseModel):
    event_date: date
    event_time: Optional[time] = None
    title: str
    type_event: CalendarStatus
    task_id: Optional[int] = None
    meeting_id: Optional[int] = None

    model_config = {
        'from_attributes': True
    }