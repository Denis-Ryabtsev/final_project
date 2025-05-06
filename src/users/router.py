from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from users.manager import fastapi_users
from users.config_token import auth_backend
from users.schemas import (
    UserRegistration, MessageResponse, UserCreate, UserInformation, UserChange, UserRead
)
from users.models import RoleType, User
from users.service import UserService
from users.depencies import get_user_service
from core_depencies import check_role
from rating.schemas import AvgRatingRead, RatingReadUser
from database import get_session


registration_router = APIRouter(prefix='/registration', tags=['Registration'])
auth_router = fastapi_users.get_auth_router(auth_backend)
operation_user = APIRouter(prefix='/users', tags=['User operations'])

@registration_router.post('', response_model=MessageResponse)
async def reg_user(
    data: UserRegistration, 
    service: UserService = Depends(get_user_service), 
    session: AsyncGenerator = Depends(get_session)
) -> MessageResponse:

    await service.register_user(session, data)

    return MessageResponse(message="Пользователь успешно зарегистрирован")

@operation_user.get('/me', response_model=UserInformation)
async def get_user(
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> Union[UserInformation, Exception]:
    
    my_profile = await service.get_user(user)

    return my_profile

@operation_user.patch('/me', response_model=UserInformation)
async def change_user(
    data: UserChange,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
) -> UserInformation:
    
    result = await service.change_user(session, user, data)

    return result

@operation_user.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    response: Response,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(fastapi_users.current_user()),
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(session, user)
    response.delete_cookie('project')

@operation_user.patch('/{user_id}/role', response_model=UserInformation)
async def change_role(
    user_id: int,
    role: RoleType,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(check_role),
    service: UserService = Depends(get_user_service)
) -> UserInformation:
    
    result = await service.change_role(session, user, user_id, role)

    return UserInformation.model_validate(result)

@operation_user.patch('/{user_id}/department', response_model=UserInformation)
async def delete_department(
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(check_role),
    service: UserService = Depends(get_user_service)
) -> UserInformation:
    
    result = await service.delete_department(session, user, user_id)

    return UserInformation.model_validate(result)

@operation_user.get('/my_rating', response_model=list[RatingReadUser])
async def get_rating(
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: UserService = Depends(get_user_service)
):
    result = await service.get_rating(session, user)

    return [RatingReadUser.model_validate(item) for item in result]

@operation_user.get("/my_avg_rating", response_model=AvgRatingRead)
async def get_quarter_avg(
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: UserService = Depends(get_user_service)
):
    return await service.get_avg_rating(session, user)