from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from tasks.models.task import Task
from tasks.models.comment import Comment
from tasks.schemas.comment import CommentCreate


class CommentService:
    """
        Сервисный слой для работы с комментариями:
            - создание комментариев
            - удаление комментариев
    """

    async def create_comment(
        self, user: User, session: AsyncSession, task_id: int, data: CommentCreate 
    ) -> Union[Comment, HTTPException]:
        """
            Создаёт нового комментария.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncSession): SQLAlchemy-сессия.
                task_id (int): Идентификатор задачи
                data (CommentCreate): Входные данные для создания комментария.
            
            Returns:
                comment (Comment): Объект комментария.
        """

        if not user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Ты должен состоять в команде'
            )
        
        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с таким id {task_id} не существует'
            )
        if target_task.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Задача не из твоей команды'
            )
        
        try:
            comment = {
                'author_id': user.id,
                'task_id': target_task.id,
                'description': data.description
            }
            comment = Comment(**comment)
            session.add(comment)
            await session.commit()
            await session.refresh(comment)

            return comment

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_comment(
        self, user: User, session: AsyncSession, task_id: int, comment_id: int
    ) -> Union[None, HTTPException]:
        """
            Удаление комментария.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncSession): SQLAlchemy-сессия.
                task_id (int): Идентификатор задачи
                comment_id (int): Идентификатор комментария.
        """

        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с таким id {task_id} не существует'
            )
        if target_task.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Задача не из твоей команды'
            )
        
        query = select(Comment).where(Comment.id == comment_id)
        target_comment = (await session.execute(query)).scalars().first()
        if not target_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Комментарий с таким id {comment_id} не существует'
            )

        try:
            await session.delete(target_comment)
            await session.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )