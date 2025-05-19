from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from tasks.models.task import Task, TaskStatus
from rating.models import Rating
from rating.schemas import RatingCreate


class RatingService:
    """
        Сервисный слой для работы с оценками задач:
            - создание оценки
    """

    async def create_rating(
        self, user: User, session: AsyncSession, task_id: int, data: RatingCreate
    ) -> Union[Rating, HTTPException]:
        """
            Создаёт новую оценку.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncSession): SQLAlchemy-сессия.
                task_id (int): Идентификатор задачи
                data (RatingCreate): Входные данные для создания оценки.
            
            Returns:
                data (Rating): Объект оценки.
        """

        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задачи с таким id {task_id} не существует'
            )
        if target_task.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Оценивать можно только задачи своей компани'
            )
        if target_task.status != TaskStatus.done:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Оценивать можно только выполненные задачи'
            )

        try:
            data = {
                'task_id': task_id,
                'owner_id': target_task.target_id,
                'head_id': user.id,
                'score_date': data.score_date,
                'score_quality': data.score_quality,
                'score_complete': data.score_complete
            }

            data = Rating(**data)
            session.add(data)
            await session.commit()
            await session.refresh(data)

            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )