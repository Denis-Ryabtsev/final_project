from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from tasks.depencies import check_company
from company.service.company import CompanyService
from tasks.schemas.task import TaskRead, TaskCreate, TaskChange, TaskChangeRole
from core_depencies import check_role, get_user
from tasks.service.task import TaskService
from tasks.models.task import TaskStatus
from tasks.depencies import get_task_service
from rating.schemas import RatingCreate, RatingRead
from rating.depencies import get_rating_service, check_rating_role
from rating.service import RatingService


rating_router = APIRouter(
    prefix='/companies/tasks/{task_id}/rating', tags=['Rating operations']
)

@rating_router.post('', response_model=RatingRead)
async def create_rating(
    task_id: int,
    data: RatingCreate,
    user: User = Depends(check_rating_role),
    session: AsyncGenerator = Depends(get_session),
    service: RatingService = Depends(get_rating_service)
):
    result = await service.create_rating(user, session, task_id, data)

    return RatingRead.model_validate(result)


# async def get_quarter_avg(
#     user: User = Depends(get_user),
#     session: AsyncGenerator = Depends(get_session),
#     service: RatingService = Depends(get_rating_service)
# ):
#     return await service.get_avg_rating(session, user)