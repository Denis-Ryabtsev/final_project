from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from tasks.schemas.task import TaskChange
from users.models import User
from company.schemas.department import DepartmentCreate
from company.models.department import Department
from tasks.models.task import Task
from tasks.models.comment import Comment
# from company.depencies import check_role


class CommentService:
    async def create_comment(
        self, user, session, task_id, data
    ):
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
        self, user, session, task_id, comment_id
    ):

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