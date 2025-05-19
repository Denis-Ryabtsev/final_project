from datetime import date, time
from typing import Optional

from pydantic import BaseModel

from calendars.models import CalendarStatus


class CalendarRead(BaseModel):
    """
        Схема для получения данных ивентов календаря

        Fields:
        - event_date: Дата события.
        - event_time: Время события.
        - title: Заголовок события
        - type_event: Тип события
        - task_id: Идентификатор задачи
        - meeting_id: Идентификатор встречи
    """

    event_date: date
    event_time: Optional[time] = None
    title: str
    type_event: CalendarStatus
    task_id: Optional[int] = None
    meeting_id: Optional[int] = None

    model_config = {
        'from_attributes': True
    }