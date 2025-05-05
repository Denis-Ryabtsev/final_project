from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users
from company.service.company import CompanyService
from company.service.department import DepartmentService
from core_depencies import check_role
from tasks.service.task import TaskService
from tasks.service.comment import CommentService


def check_company(
    user: User = Depends(check_role)
):
    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нужно наличие компании'
        )
    
    return user

def get_task_service() -> TaskService:
    return TaskService()

def get_comment_service() -> CommentService:
    return CommentService()