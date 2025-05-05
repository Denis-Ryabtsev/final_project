from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from tasks.depencies import check_company
from company.service.company import CompanyService
from tasks.schemas.task import TaskRead, TaskCreate, TaskChange, TaskChangeRole
from tasks.schemas.comment import CommentCreate, CommentRead
from core_depencies import check_role, get_user
from tasks.service.task import TaskService
from tasks.service.comment import CommentService
from tasks.models.task import TaskStatus
from tasks.depencies import get_task_service, get_comment_service


comment_router = APIRouter(
    prefix='/companies/tasks/{task_id}/comments', tags=['Comments operations']
)

@comment_router.post('', response_model=CommentRead)
async def comment_create(
    task_id: int,
    data: CommentCreate,
    user: User = Depends(get_user),
    session: AsyncGenerator = Depends(get_session),
    service: CommentService = Depends(get_comment_service)
):
    result = await service.create_comment(user, session, task_id, data)

    return CommentRead.model_validate(result)

@comment_router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def comment_create(
    task_id: int,
    comment_id: int,
    user: User = Depends(check_company),
    session: AsyncGenerator = Depends(get_session),
    service: CommentService = Depends(get_comment_service)
):
    
    await service.delete_comment(user, session, task_id, comment_id)