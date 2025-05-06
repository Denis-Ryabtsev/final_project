import datetime
from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import func, select

from tasks.schemas.task import TaskChange
from users.models import User
from company.schemas.department import DepartmentCreate
from company.models.department import Department
from tasks.models.task import Task, TaskStatus
from rating.models import Rating
from rating.schemas import AvgRatingRead
# from company.depencies import check_role


class RatingService:
    async def create_rating(
        self, user, session, task_id, data
    ):
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
    
#     async def get_avg_rating(
#         self, session: AsyncGenerator, user: User
# ):
#         # Определяем начало текущего квартала
#         today = datetime.utcnow().date()
#         quarter = (today.month - 1) // 3 + 1
#         quarter_start_month = 3 * (quarter - 1) + 1
#         quarter_start = datetime(today.year, quarter_start_month, 1).date()

#         # Строим запрос
#         query = (
#             select(
#                 func.avg(Rating.score_date).label("avg_date"),
#                 func.avg(Rating.score_quality).label("avg_quality"),
#                 func.avg(Rating.score_complete).label("avg_complete"),
#             )
#             .where(
#                 Rating.owner_id == user.id,
#                 Rating.created_at >= quarter_start,
#             )
#         )

#         result = await session.execute(query)
#         row = result.mappings().first() or {}
#         return AvgRatingRead(**row)