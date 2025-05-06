from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from company.depencies import get_company_service
from company.service.company import CompanyService
from core_depencies import check_role
from meeting.schemas import MeetingCreate, MeetingRead, MeetingChange, MeetingResponse
from meeting.depencies import check_company_role_meeting
from meeting.service import MeetingService
from meeting.depencies import get_meeting_service
# from calendars.schemas
# from calendars.schemas import CalendarRead


meeting_router = APIRouter(
    prefix='/meeting', tags=['Meeting operations']
)

@meeting_router.post('', response_model=MeetingRead)
async def create_meeting(
    data: MeetingCreate,
    user: User = Depends(check_company_role_meeting),
    session: AsyncGenerator = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
):
    result = await service.create_meeting(user, session, data)

    return MeetingRead.model_validate(result)

@meeting_router.delete('/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    user: User = Depends(check_company_role_meeting),
    session: AsyncGenerator = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
):
    await service.delete_meeting(user, session, meeting_id)

@meeting_router.patch('/{meeting_id}', response_model=MeetingRead)
async def change_meeting(
    meeting_id: int,
    data: MeetingChange,
    user: User = Depends(check_company_role_meeting),
    session: AsyncGenerator = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
):
    result = await service.change_meeting(user, session, meeting_id, data)
    return MeetingRead.model_validate(result)

@meeting_router.post('/{meeting_id}', response_model=MeetingResponse)
async def add_user_meeting(
    meeting_id: int,
    user_id: int,
    user: User = Depends(check_company_role_meeting),
    session: AsyncGenerator = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
):
    service.add_user_meeting(user, session, meeting_id, user_id)
    return MeetingResponse(message='Пользователь успешно добавлен')