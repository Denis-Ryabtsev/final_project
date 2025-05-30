from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from rating.schemas import RatingCreate, RatingRead
from rating.depencies import get_rating_service, check_rating_role
from rating.service import RatingService


rating_router = APIRouter(
    prefix='/companies/tasks/{task_id}/ratings', tags=['Ratings']
)

@rating_router.post('', response_model=RatingRead)
async def create_rating(
    task_id: int,
    data: RatingCreate,
    user: User = Depends(check_rating_role),
    session: AsyncSession = Depends(get_session),
    service: RatingService = Depends(get_rating_service)
) -> Union[RatingRead, Exception]:
    """
        Создание оценки задачи.

        Args:
            data (RatingCreate): Входные данные для создания оценки.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (RatingService): Сервис для создания оценок.
            
        Returns:
            RatingRead: Схема для вывода созданной оценки.
    """

    created_rate = await service.create_rating(user, session, task_id, data)

    return RatingRead.model_validate(created_rate)