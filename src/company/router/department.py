from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from company.depencies import get_department_service
from company.service.department import DepartmentService
from company.schemas.department import DepartmentRead, DepartmentCreate
from company.depencies import validate_company_presence


department_router = APIRouter(
    prefix='/companies/departments', tags=['Departments']
)

@department_router.post('', response_model=DepartmentRead)
async def create_department(
    data: DepartmentCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_company_presence),
    service: DepartmentService = Depends(get_department_service)
) -> Union[DepartmentRead, Exception]:
    """
        Создание отдела компании.

        Args:
            company_id (int): Идентификатор компании
            data (DepartmentCreate): Входные данные для создания отделов
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
            
        Returns:
            DepartmentRead: Схема для получения данных отдела.
    """

    result = await service.create_department(session, user, user.company_id, data)

    return DepartmentRead.model_validate(result)

@department_router.patch(
    '/{department_id}', response_model=DepartmentRead
)
async def set_department_head(
    department_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_company_presence),
    service: DepartmentService = Depends(get_department_service)
) -> Union[DepartmentRead, Exception]:
    """
        Изменение руководителя отдела.

        Args:
            company_id (int): Идентификатор компании
            department_id (int): Идентификатор отдела
            user_id (int): Идентификатор пользователя
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
            
        Returns:
            DepartmentRead: Схема для получения данных отдела.
    """

    result = await service.change_head_user(
        session, user, user.company_id, department_id, user_id
    )

    return DepartmentRead.model_validate(result)

@department_router.delete('/{department_id}', status_code=204)
async def delete_department(
    department_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(validate_company_presence),
    service: DepartmentService = Depends(get_department_service)
) -> None:
    """
        Удаление отдела компании.

        Args:
            company_id (int): Идентификатор компании
            department_id (int): Идентификатор отдела
            session (AsyncSession): SQLAlchemy-сессия.
            user (User): Получение текущего пользователя.
            service (DepartmentService): Сервис для создания отдела.
    """

    await service.delete_department(session, user, user.company_id, department_id)
