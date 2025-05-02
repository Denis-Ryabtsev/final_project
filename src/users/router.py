from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from users.manager import fastapi_users
from users.config_token import auth_backend
from users.schemas import (
    UserRegistration, MessageResponse, UserCreate, UserInformation, UserChange, UserRead
)
from users.models import User
from users.service import UserService
from users.depencies import get_user_service
from database import get_session


registration_router = APIRouter(prefix='/registration', tags=['Registration'])
auth_router = fastapi_users.get_auth_router(auth_backend)
operation_user = APIRouter(prefix='/users', tags=['User operations'])

@registration_router.post('', response_model=MessageResponse)
async def reg_user(
    data: UserRegistration, service: UserService = Depends(get_user_service)
) -> MessageResponse:

    user = UserCreate(**data.model_dump())
    await service.register_user(user)

    return MessageResponse(message="Пользователь успешно зарегистрирован")

@operation_user.get('', response_model=UserInformation)
async def get_user(
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> Union[UserInformation, Exception]:
    
    my_profile = await service.get_user(user)

    return my_profile

@operation_user.patch('', response_model=UserRead)
async def change_user(
    data: UserChange,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> UserRead:
    
    result = await service.change_user(session, user, data)

    return result

@operation_user.delete('', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    response: Response,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(session, user)
    response.delete_cookie('project')