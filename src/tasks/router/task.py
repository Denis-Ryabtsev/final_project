from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status

from database import get_session
from users.models import User
from tasks.depencies import check_company
from tasks.schemas.task import TaskRead, TaskCreate, TaskChange, TaskChangeRole
from core_depencies import get_user
from tasks.service.task import TaskService
from tasks.depencies import get_task_service


task_router = APIRouter(
    prefix='/companies/tasks', tags=['Tasks operations']
)

@task_router.post('', response_model=TaskRead)
async def create_task(
    data: TaskCreate,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Создаёт новой задачи и занесения ее в календарь пользователя.

        Args:
            data (TaskCreate): Входные данные для создания задачи.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    result = await service.create_task(user, session, data)
    await service.add_task_calendar(session, result)
    
    return TaskRead(**result)

@task_router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[None, Exception]:
    """
        Создаёт новой задачи и занесения ее в календарь пользователя.

        Args:
            task_id (int): Идентификатор задачи.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
    """

    await service.delete_task(user, task_id, session)

@task_router.patch('/{task_id}', response_model=TaskRead)
async def change_task(
    task_id: int,
    data: TaskChange,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Создаёт новой задачи и занесения ее в календарь пользователя.

        Args:
            task_id (int): Идентификатор задачи
            data (TaskChange): Входные данные для изменения задачи.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    result = await service.change_task(user, session, data, task_id)

    return TaskRead.model_validate(result)

@task_router.patch('/{task_id}/status', response_model=TaskRead)
async def change_task_role(
    task_id: int,
    task_status: TaskChangeRole,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
) -> Union[TaskRead, Exception]:
    """
        Создаёт новой задачи и занесения ее в календарь пользователя.

        Args:
            task_id (int): Идентификатор задачи
            task_status (TaskChangeRole): Тип статуса задачи.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (TaskService): Сервис для создания пользователя.
                        
        Returns:
            TaskRead: Схема для получения созданной задачи.
    """

    result = await service.change_task_role(user, session, task_id, task_status)

    return TaskRead.model_validate(result)