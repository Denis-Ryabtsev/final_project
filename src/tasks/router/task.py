from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from tasks.depencies import check_company
from company.service.company import CompanyService
from tasks.schemas.task import TaskRead, TaskCreate, TaskChange, TaskChangeRole, TaskResponse
from core_depencies import check_role, get_user
from tasks.service.task import TaskService
from tasks.models.task import TaskStatus
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
):
    result = await service.create_task(user, session, data)
    await service.add_task_calendar(session, result)
    
    return TaskRead(**result)
    # return TaskRead.model_validate(result)
    # return TaskResponse(message='Задача создана успешно')

@task_router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
):
    await service.delete_task(user, task_id, session)

@task_router.patch('/{task_id}', response_model=TaskRead)
async def change_task(
    task_id: int,
    data: TaskChange,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
):
    result = await service.change_task(user, session, data, task_id)

    return TaskRead.model_validate(result)

@task_router.patch('/my/{task_id}', response_model=TaskRead)
async def change_task_role(
    task_id: int,
    task_status: TaskChangeRole,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: TaskService = Depends(get_task_service)
):
    result = await service.change_task_role(user, session, task_id, task_status)

    return TaskRead.model_validate(result)