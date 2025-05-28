from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from tasks.depencies import check_company
from tasks.schemas.task import TaskRead, TaskCreate, TaskChange, TaskChangeRole
from core_depencies import get_user
from tasks.service.task import TaskService
from tasks.depencies import get_task_service


task_router = APIRouter(
    prefix='/companies/tasks', tags=['Tasks']
)

@task_router.post('', response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    user: User = Depends(check_company),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Создание новой задачи и занесения ее в календарь пользователя.

        Args:
            data (TaskCreate): Входные данные для создания задачи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    created_task = await service.create_task(user, session, data)
    await service.add_task_calendar(session, created_task)
    
    return TaskRead(**created_task)

@task_router.delete('/{task_id}', status_code=204)
async def delete_task(
    task_id: int,
    user: User = Depends(check_company),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> None:
    """
        Удаления задачи

        Args:
            task_id (int): Идентификатор задачи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
    """

    await service.delete_task(user, task_id, session)

@task_router.patch('/{task_id}', response_model=TaskRead)
async def change_task(
    data: TaskChange,
    task_id: int,
    user: User = Depends(check_company),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Изменения задачи

        Args:
            task_id (int): Идентификатор задачи
            data (TaskChange): Входные данные для изменения задачи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    changed_task = await service.change_task(user, session, data, task_id)

    return TaskRead.model_validate(changed_task)

@task_router.patch('/{task_id}/status', response_model=TaskRead)
async def change_task_role(
    task_status: TaskChangeRole,
    task_id: int,
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Изменение статуса задачи

        Args:
            task_id (int): Идентификатор задачи
            task_status (TaskChangeRole): Тип статуса задачи.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    changed_task = await service.change_task_role(user, session, task_id, task_status)

    return TaskRead.model_validate(changed_task)