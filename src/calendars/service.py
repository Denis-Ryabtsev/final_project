from datetime import date
from typing import AsyncGenerator, Union

from fastapi import HTTPException, status, Depends
from sqlalchemy import extract, select

from calendars.schemas import CalendarRead
from users.models import User
from company.schemas.company import CompanyCreate, CompanyRead
from company.models.company import Company
from calendars.models import Calendar
# from company.depencies import check_role


class CalendarService:
    """
        Сервисный слой для работы с календарем:
            - отображение дневного расписания
            - отображение месячного расписания
    """

    async def get_day_schedule(
    self, user: User, session: AsyncGenerator, day: int
) -> Union[Calendar, list[Calendar]]:
        """
            Получение дневного расписания.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                day (int): Номер дня

            Returns:
                list[Calendar] (Calendar): Список объектов Calendar.
        """

        today = date.today()
        query = (
            select(Calendar)
            .where(
                Calendar.user_id == user.id,
                extract('day', Calendar.event_date) == day,
                extract('month', Calendar.event_date) == today.month,
                extract('year', Calendar.event_date) == today.year
            )
            .order_by(Calendar.event_time)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_month_schedule(
        self, session: AsyncGenerator, user, year: int, month: int
    ) -> Union[Calendar, list[Calendar]]:
        """
            Получение месячного расписания.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                year (int): Номер года
                month (int): Номер месяца

            Returns:
                list[Calendar] (Calendar): Список объектов Calendar.
        """

        query = (
            select(Calendar)
            .where(
                Calendar.user_id == user.id,
                extract('year', Calendar.event_date) == year,
                extract('month', Calendar.event_date) == month,
                extract('day', Calendar.event_date) >= 1
            )
            .order_by(Calendar.event_date, Calendar.event_time)
        )
        result = await session.execute(query)
        events = result.scalars().all()
        return [CalendarRead.model_validate(event) for event in events]