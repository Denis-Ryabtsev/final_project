import datetime
from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from calendars.depencies import get_calendar_service
from calendars.service import CalendarService
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from company.depencies import get_company_service
from company.service.company import CompanyService
from core_depencies import check_role, get_user
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
):
    schedule = await service.get_day_schedule(user, session, day)
    return [CalendarRead.model_validate(item) for item in schedule]

@calendar_router.get('/month', response_model=list[CalendarRead])
async def get_month_schedule(
    year: int,
    month: int,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: CalendarService = Depends()
):
    return await service.get_month_schedule(session, user, year, month)