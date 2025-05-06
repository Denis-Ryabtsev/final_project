from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users
from company.service.company import CompanyService
from company.service.department import DepartmentService
from core_depencies import check_role, get_user
from tasks.service.task import TaskService
from tasks.service.comment import CommentService
from rating.service import RatingService
from meeting.service import MeetingService


def check_company_role_meeting(
    user: User = Depends(get_user)
):
    if user == RoleType.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Создавать встречи может только менеджер или админ'
        )
    elif not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Чтобы создавать встречи, нужно находится в команде'
        )
    
    return user

def get_meeting_service() -> MeetingService:
    return MeetingService()