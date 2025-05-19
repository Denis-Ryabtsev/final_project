from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from tasks.depencies import check_company
from tasks.schemas.comment import CommentCreate, CommentRead
from core_depencies import get_user
from tasks.service.comment import CommentService
from tasks.depencies import get_comment_service


comment_router = APIRouter(
    prefix='/companies/tasks/{task_id}/comments', tags=['Comments']
)

@comment_router.post('', response_model=CommentRead)
async def comment_create(
    task_id: int,
    data: CommentCreate,
    user: User = Depends(get_user),
    session: AsyncSession = Depends(get_session),
    service: CommentService = Depends(get_comment_service)
) -> Union[CommentRead, Exception]:
    """
        Создаёт новый комментарий.

        Args:
            data (CommentCreate): Входные данные для создания комментария.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (CommentService): Сервис для создания комментария.
        
        Returns:
            CommentRead: Информация о комментарии.
    """

    result = await service.create_comment(user, session, task_id, data)

    return CommentRead.model_validate(result)

@comment_router.delete('/{comment_id}', status_code=204)
async def comment_delete(
    task_id: int,
    comment_id: int,
    user: User = Depends(check_company),
    session: AsyncSession = Depends(get_session),
    service: CommentService = Depends(get_comment_service)
) -> None:
    """
        Удаление комментария.

        Args:
            task_id (int): Идентификатор задачи.
            comment_id (int): Идентификатор комментария.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (CommentService): Сервис для создания комментария.
    """

    await service.delete_comment(user, session, task_id, comment_id)