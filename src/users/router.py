from typing import Union

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from users.manager import fastapi_users
from users.config_token import auth_backend
from users.schemas import (
    UserRegistration, MessageResponse, UserInformation, UserChange
)
from users.models import RoleType, User
from users.service import UserService
from users.depencies import get_user_service
from core_depencies import check_role
from rating.schemas import AvgRatingRead, RatingReadUser
from tasks.schemas.task import TaskRead
from database import get_session


registration_router = APIRouter(prefix='/registration', tags=['Registration'])
auth_user_router = fastapi_users.get_auth_router(auth_backend)
operation_user = APIRouter(prefix='/users', tags=['Users'])


@registration_router.post('', response_model=MessageResponse)
async def reg_user(
    data: UserRegistration, 
    service: UserService = Depends(get_user_service), 
    session: AsyncSession = Depends(get_session)
) -> MessageResponse:
    """
        Создаёт нового пользователя.

        Args:
            data (UserRegistration): Входные данные для создания пользователя.
            service (UserService): Сервис для создания пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            
        Returns:
            MessageResponse: Сообщение об успешном выполнении.
    """
    
    await service.register_user(session, data)

    return MessageResponse(message="Пользователь успешно зарегистрирован")

@operation_user.get('/me', response_model=UserInformation)
async def get_user(
    user: User = Depends(fastapi_users.current_user())
) -> Union[UserInformation, Exception]:
    """
        Получение информации о профиле.

        Args:
            user (User): Получение текущего пользователя.
            
        Returns:
            UserInformation: Информация о пользователе.
    """

    return UserInformation.model_validate(user)

@operation_user.patch('/me', response_model=UserInformation)
async def change_user(
    data: UserChange,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> Union[UserInformation, Exception]:
    """
        Изменение профиля пользователя.

        Args:
            data (UserChange): Входные данные для изменения пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (UserService): Сервис для создания пользователя.
            
        Returns:
            UserInformation: Информация о пользователе.
    """
    
    changed_user = await service.change_user(session, user, data)

    return changed_user

@operation_user.delete('/me', status_code=204)
async def delete_user(
    response: Response,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> None:
    """
        Удаление пользователя.

        Args:
            response (Response): Ответ от сервера
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (UserService): Сервис для создания пользователя.
            
    """
    
    await service.delete_user(session, user)
    response.delete_cookie('project')

@operation_user.patch('/{user_id}/role', response_model=UserInformation)
async def change_role(
    user_id: int,
    role: RoleType,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(check_role),
    service: UserService = Depends(get_user_service)
) -> Union[UserInformation, Exception]:
    """
        Изменение роли пользователя админом.

        Args:
            user_id (int): Идентификатор пользователя
            role (RoleType): Тип роли.
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (UserService): Сервис для создания пользователя.
            
        Returns:
            UserInformation: Информация о пользователе.
    """
    
    changed_user = await service.change_role(session, user, user_id, role)

    return UserInformation.model_validate(changed_user)

@operation_user.patch('/{user_id}/department', response_model=UserInformation)
async def delete_department(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(check_role),
    service: UserService = Depends(get_user_service)
) -> Union[UserInformation, Exception]:
    """
        Удаление отдела у пользователя.

        Args:
            user_id (int): Идентификатор пользователя
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (UserService): Сервис для создания пользователя.
            
        Returns:
            UserInformation: Информация о пользователе.
    """

    changed_user = await service.delete_department(session, user, user_id)

    return changed_user

@operation_user.get('/me/rating', response_model=list[RatingReadUser])
async def get_rating(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service)
) -> list[RatingReadUser]:
    """
        Получение оценок задач.

        Args:
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (UserService): Сервис для создания пользователя.
            
        Returns:
            RatingReadUser (list[RatingReadUser]): Информация об оценках задач.
    """

    my_rating = await service.get_rating(session, user)

    return [RatingReadUser.model_validate(item) for item in my_rating]

@operation_user.get("/me/ratings/average", response_model=AvgRatingRead)
async def get_quarter_avg(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service)
) -> AvgRatingRead:
    """
        Получение средних значений оценок задач.

        Args:
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (UserService): Сервис для создания пользователя.
            
        Returns:
            AvgRatingRead: Информация об средних оценках задач.
    """

    return await service.get_avg_rating(session, user)

@operation_user.get('/me/tasks', response_model=list[TaskRead])
async def get_my_tasks(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service)
) -> list[TaskRead]:
    """
        Получение назначенных задач.

        Args:
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (UserService): Сервис для создания пользователя.

        Returns:
            result (list[Task]): Список назначенных задач.
            
    """
    
    user_tasks = await service.get_my_tasks(user, session)

    return TaskRead.model_validate(user_tasks)

@operation_user.get('/me/tasks_owner', response_model=list[TaskRead])
async def get_my_tasks(
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service)
) -> list[TaskRead]:
    """
        Получение выданных задач.

        Args:
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.

        Returns:
            result (list[Task]): Список выданных задач.
        
    """
    
    owner_tasks = await service.get_owner_tasks(user, session)

    return TaskRead.model_validate(owner_tasks)