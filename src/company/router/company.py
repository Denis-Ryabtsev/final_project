from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from company.depencies import get_company_service
from company.service.company import CompanyService
from core_depencies import check_role, get_user


company_router = APIRouter(
    prefix='/companies', tags=['Company operations']
)

@company_router.post('', response_model=CompanyRead)
async def create_company(
    data: CompanyCreate,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
) -> Union[CompanyRead, Exception]:
    """
        Создаёт новой компании.

        Args:
            data (CompanyCreate): Входные данные для создания компании.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CompanyService): Сервис для создания компании.
            user (User): Получение текущего пользователя.
            
        Returns:
            company (CompanyRead): Схема для получения данных компании.
    """
    
    company = await service.create_company(session, data, user)

    return CompanyRead.model_validate(company)

@company_router.post('/{company_id}/users', response_model=UserInformation)
async def add_user(
    company_id: int,
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
) -> Union[UserInformation, Exception]:
    """
        Добавление пользователей в компанию.

        Args:
            company_id (int): Идентификатор компании
            user_id (int): Идентификатор пользователя
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CompanyService): Сервис для создания компании.
            user (User): Получение текущего пользователя.
            
        Returns:
            UserInformation: Схема для получения данных пользователя.
    """

    add_user = await service.add_user(session, company_id, user_id)

    return UserInformation.model_validate(add_user)

@company_router.patch('/{company_id}/users/{user_id}', response_model=UserInformation)
async def delete_user(
    company_id: int,
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
) -> Union[UserInformation, Exception]:
    """
        Удаление пользователей из компании.

        Args:
            company_id (int): Идентификатор компании
            user_id (int): Идентификатор пользователя
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CompanyService): Сервис для создания компании.
            user (User): Получение текущего пользователя.
            
        Returns:
            UserInformation: Схема для получения данных пользователя.
    """

    add_user = await service.delete_user(session, company_id, user_id)

    return UserInformation.model_validate(add_user)

@company_router.delete('/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
) -> None:
    """
        Удаление компании.

        Args:
            company_id (int): Идентификатор компании
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CompanyService): Сервис для создания компании.
            user (User): Получение текущего пользователя.
    """

    await service.delete_company(session, company_id)

@company_router.get('/{company_id}/users', response_model=list[UserInformation])
async def get_company_users(
    company_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(get_user)
) -> list[UserInformation]:
    """
        Получение пользователей компании.

        Args:
            company_id (int): Идентификатор компании
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (CompanyService): Сервис для создания компании.
            user (User): Получение текущего пользователя.
            
        Returns:
            result (list[UserInformation]): Схема для получения данных пользователя.
    """ 
    
    result = await service.get_company_users(session, user, company_id)

    return result