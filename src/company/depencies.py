from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users
from company.service.company import CompanyService
from company.service.department import DepartmentService
from core_depencies import check_role


def get_company_service() -> CompanyService:
    return CompanyService()

def get_department_service() -> DepartmentService:
    return DepartmentService()

def check_company(
    user: User = Depends(check_role)
):
    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Создавать оргструктуру можно при наличии команды'
        )
    
    return user