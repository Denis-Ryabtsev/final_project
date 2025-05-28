from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from company.depencies import validate_company_presence
from meeting.schemas import MeetingCreate, MeetingRead, MeetingChange, MeetingResponse
from meeting.depencies import check_company_role_meeting
from meeting.service import MeetingService
from meeting.depencies import get_meeting_service


meeting_router = APIRouter(
    prefix='/meeting', tags=['Meetings']
)

@meeting_router.post('', response_model=MeetingRead)
async def create_meeting(
    data: MeetingCreate,
    user: User = Depends(check_company_role_meeting),
    session: AsyncSession = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
) -> Union[MeetingRead, Exception]:
    """
        Создаёт новую встречу.

        Args:
            data (MeetingCreate): Входные данные для создания встречи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (MeetingService): Сервис для создания встреч.
            
        Returns:
            MeetingRead: Схема для отображения встречи.
    """

    result = await service.create_meeting(user, session, data)

    return MeetingRead.model_validate(result)

@meeting_router.delete('/{meeting_id}', status_code=204)
async def delete_meeting(
    meeting_id: int,
    user: User = Depends(check_company_role_meeting),
    session: AsyncSession = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
) -> None:
    """
        Удаляет встречу.

        Args:
            meeting_id (int): Идентификатор встречи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (MeetingService): Сервис для создания встреч.
    """

    await service.delete_meeting(user, session, meeting_id)

@meeting_router.patch('/{meeting_id}', response_model=MeetingRead)
async def change_meeting(
    meeting_id: int,
    data: MeetingChange,
    user: User = Depends(check_company_role_meeting),
    session: AsyncSession = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
) -> Union[MeetingRead, Exception]:
    """
        Изменяет встречу.

        Args:
            meeting_id (int): Идентификатор встречи.
            data (MeetingChange): Входные данные для изменения встречи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (MeetingService): Сервис для создания встреч.
            
        Returns:
            MeetingRead: Схема для отображения встречи.
    """

    result = await service.change_meeting(user, session, meeting_id, data)
    return MeetingRead.model_validate(result)

@meeting_router.post('/{meeting_id}/participants', response_model=MeetingResponse)
async def add_user_meeting(
    meeting_id: int,
    user_id: int,
    user: User = Depends(check_company_role_meeting),
    session: AsyncSession = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
) -> Union[MeetingResponse, Exception]:
    """
        Добавление пользователей на встречу.

        Args:
            meeting_id (int): Идентификатор встречи.
            user_id (int): Идентификатор пользователя.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (MeetingService): Сервис для создания встреч.
            
        Returns:
            MeetingResponse: Схема для ответа эндпоинта.
    """
    
    service.add_user_meeting(user, session, meeting_id, user_id)
    return MeetingResponse(message='Пользователь успешно добавлен')

@meeting_router.get('', response_model=list[MeetingRead])
async def get_owner_meeting(
    user: User = Depends(validate_company_presence),
    session: AsyncSession = Depends(get_session),
    service: MeetingService = Depends(get_meeting_service)
) -> list[MeetingRead]:
    """
        Получение списка встреч.

        Args:
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (MeetingService): Сервис для создания встреч.
            
        Returns:
            MeetingRead: Схема для отображения встречи.
    """

    result = service.get_meeting(user, session, user.company_id)

    return MeetingRead.model_validate(result)
