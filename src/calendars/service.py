from datetime import date
from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import extract, select

from calendars.schemas import CalendarRead
from users.models import User
from company.schemas.company import CompanyCreate, CompanyRead
from company.models.company import Company
from calendars.models import Calendar
# from company.depencies import check_role


class CalendarService:
    async def get_day_schedule(
    self, user, session: AsyncGenerator, day: int
):
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
    ) -> list[CalendarRead]:
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