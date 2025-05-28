from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from calendars.depencies import get_calendar_service
from calendars.service import CalendarService
from users.models import User
from core_depencies import get_user
from calendars.schemas import CalendarRead


calendar_router = APIRouter(
    prefix='/calendar/my', tags=['Calendars']
)

@calendar_router.get('/day', response_model=list[CalendarRead])
async def get_schedule_for_day(
    day: int,
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: CalendarService = Depends(get_calendar_service)
) -> Union[list[CalendarRead], Exception]:
    """
        Получение дневного расписания.

        Args:
            day (int): Номер дня для составления дневного расписания
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
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
    session: AsyncSession = Depends(get_session),
    service: CalendarService = Depends()
) -> Union[list[CalendarRead], Exception]:
    """
        Получение месячного расписания.

        Args:
            year (int): Год для составления месячного расписания
            month (int): Месяц для составления месячного расписания
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (CalendarService): Сервис для работы календаря.
            
        Returns:
            CalendarRead: Схема для отображения событий.
    """

    schedule = await service.get_month_schedule(session, user, year, month)
    
    return [CalendarRead.model_validate(item) for item in schedule]