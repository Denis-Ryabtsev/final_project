from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from company.depencies import get_company_service
from company.service.company import CompanyService
from core_depencies import check_role

company_router = APIRouter(
    prefix='/companies', tags=['Company operations']
)

@company_router.post('', response_model=CompanyRead)
async def create_company(
    data: CompanyCreate,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
):
    company = await service.create_company(session, data)

    return company

@company_router.post('/{company_id}/users', response_model=UserInformation)
async def add_user(
    company_id: int,
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
):
    add_user = await service.add_user(session, company_id, user_id)

    return UserInformation.model_validate(add_user)

@company_router.delete('/{company_id}/users/{user_id}', response_model=UserInformation)
async def delete_user(
    company_id: int,
    user_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
):
    add_user = await service.delete_user(session, company_id, user_id)

    return UserInformation.model_validate(add_user)

@company_router.delete('/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    session: AsyncGenerator = Depends(get_session),
    service: CompanyService = Depends(get_company_service),
    user: User = Depends(check_role) 
):
    await service.delete_company(session, company_id)
