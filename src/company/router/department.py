from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status

from database import get_session
from users.models import User
from company.depencies import get_department_service
from company.service.department import DepartmentService
from company.schemas.department import DepartmentRead, DepartmentCreate
from company.depencies import check_company


department_router = APIRouter(
    prefix='/companies', tags=['Department operations']
)

@department_router.post('/{company_id}/departments', response_model=DepartmentRead)
async def create_department(
    company_id: int,
    data: DepartmentCreate,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(check_company),
    service: DepartmentService = Depends(get_department_service)
) -> Union[DepartmentRead, Exception]:
    """
        Создание отделов компании.

        Args:
            company_id (int): Идентификатор компании
            data (DepartmentCreate): Входные данные для создания отделов
            session (AsyncGenerator): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
            
        Returns:
            DepartmentRead: Схема для получения данных отдела.
    """

    result = await service.create_department(session, user, company_id, data)

    return DepartmentRead.model_validate(result)

@department_router.patch('/{company_id}/departments/{department_id}', response_model=DepartmentRead)
async def change_department_head_user(
    company_id: int,
    department_id: int,
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(check_company),
    service: DepartmentService = Depends(get_department_service)
) -> Union[DepartmentRead, Exception]:
    """
        Изменение руководителя отдела.

        Args:
            company_id (int): Идентификатор компании
            department_id (int): Идентификатор отдела
            user_id (int): Идентификатор пользователя
            session (AsyncGenerator): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
            
        Returns:
            DepartmentRead: Схема для получения данных отдела.
    """

    result = await service.change_head_user(session, user, company_id, department_id, user_id)

    return DepartmentRead.model_validate(result)

@department_router.delete('/{company_id}/departments/{department_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    company_id: int,
    department_id: int,
    session: AsyncGenerator = Depends(get_session),
    user: User = Depends(check_company),
    service: DepartmentService = Depends(get_department_service)
) -> Union[None, Exception]:
    """
        Удаление отдела компании.

        Args:
            company_id (int): Идентификатор компании
            department_id (int): Идентификатор отдела
            session (AsyncGenerator): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
    """

    await service.delete_department(session, user, company_id, department_id)
