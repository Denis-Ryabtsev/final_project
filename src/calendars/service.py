from datetime import date
from typing import Union
from calendar import monthrange

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from calendars.models import Calendar



class CalendarService:
    """
        Сервисный слой для работы с календарем:
            - отображение дневного расписания
            - отображение месячного расписания
    """

    async def get_day_schedule(
    self, user: User, session: AsyncSession, day: int
) -> Union[list[Calendar]]:
        """
            Получение дневного расписания.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncSession): SQLAlchemy-сессия.
                day (int): Номер дня

            Returns:
                list[Calendar] (Calendar): Список объектов Calendar.
        """

        today = date.today()
        target_date = date(today.year, today.month, day)

        query = (
            select(Calendar)
            .where(
                Calendar.user_id == user.id,
                Calendar.event_date == target_date
            )
            .order_by(Calendar.event_time)
        )
        result = await session.execute(query)

        return result.scalars().all()
    
    async def get_month_schedule(
        self, session: AsyncSession, user: User, year: int, month: int
    ) -> Union[list[Calendar]]:
        """
            Получение месячного расписания.

            Args:
                session (AsyncSession): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                year (int): Номер года
                month (int): Номер месяца

            Returns:
                list[Calendar] (Calendar): Список объектов Calendar.
        """

        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        query = (
            select(Calendar)
            .where(
                Calendar.user_id == user.id,
                Calendar.event_date >= start_date,
                Calendar.event_date <= end_date
            )
            .order_by(Calendar.event_date, Calendar.event_time)
        )
        result = await session.execute(query)
        return result.scalars().all()