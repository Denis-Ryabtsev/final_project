from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends

from database import get_session
from calendars.depencies import get_calendar_service
from calendars.service import CalendarService
from users.models import User
from core_depencies import get_user
from calendars.schemas import CalendarRead


calendar_router = APIRouter(
    prefix='/calendar/my', tags=['Calendar operations']
)

@calendar_router.get('/day', response_model=list[CalendarRead])
async def get_schedule_for_day(
    day: int,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: CalendarService = Depends(get_calendar_service)
) -> Union[CalendarRead, Exception]:
    """
        Получение дневного расписания.

        Args:
            day (int): Номер дня для составления дневного расписания
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CalendarService): Сервис для работы календаря.
            
        Returns:
            CalendarRead: Схема для отображения событий.
    """

    schedule = await service.get_day_schedule(user, session, day)
    return [CalendarRead.model_validate(item) for item in schedule]

@calendar_router.get('/month', response_model=list[CalendarRead])
async def get_month_schedule(
    year: int,
    month: int,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: CalendarService = Depends()
) -> Union[CalendarRead, Exception]:
    """
        Получение месячного расписания.

        Args:
            year (int): Год для составления месячного расписания
            month (int): Месяц для составления месячного расписания
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CalendarService): Сервис для работы календаря.
            
        Returns:
            CalendarRead: Схема для отображения событий.
    """

    return await service.get_month_schedule(session, user, year, month)