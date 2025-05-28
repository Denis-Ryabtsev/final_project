from fastapi import Depends, HTTPException, status

from users.models import User
from company.service.company import CompanyService
from company.service.department import DepartmentService
from core_depencies import check_role


#   возврат сервиса компании
def get_company_service() -> CompanyService:
    return CompanyService()

#   возврат сервиса отдела
def get_department_service() -> DepartmentService:
    return DepartmentService()

#   проверка а принадлежность к компании
def validate_company_presence(
    user: User = Depends(check_role)
):
    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Создавать оргструктуру можно при наличии компании'
        )
    
    return user