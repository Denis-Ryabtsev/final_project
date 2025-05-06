from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users
from company.service.company import CompanyService
from company.service.department import DepartmentService
from core_depencies import check_role, get_user
from tasks.service.task import TaskService
from tasks.service.comment import CommentService
from rating.service import RatingService


def get_rating_service() -> RatingService:
    return RatingService()

def check_rating_role(
    user: User = Depends(get_user)
):
    if user == RoleType.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Оценивать может только админ или менеджер'
        )
    
    return user