from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from users.models import User
from company.schemas.company import CompanyCreate, CompanyRead
from company.models.company import Company
# from company.depencies import check_role


class CompanyService:

    async def create_company(
        self, session: AsyncGenerator, data: CompanyCreate
    ):
        query = select(Company).where(Company.name == data.name)
        result = (await session.execute(query)).scalars().first()

        if result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Компания {data.name} уже существует'
            )
        
        try:
            new_company = Company(**data.model_dump())
            session.add(new_company)
            await session.commit()
            await session.refresh(new_company)
            return CompanyRead.model_validate(new_company)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def add_user(
        self, session: AsyncGenerator, company_id: int, user_id: int
    ):
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Компания с id {company_id} не существует'
            )
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не существует'
            )
        
        try:
            user.company_id = company.id
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_user(
        self, session: AsyncGenerator, company_id: int, user_id: int
    ):
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Компания с id {company_id} не существует'
            )
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не существует'
            )
        
        try:
            user.company_id = None
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def delete_company(
        self, session: AsyncGenerator, company_id: int
    ):
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Компания с id {company_id} не существует'
            )
        
        try:
            await session.delete(company)
            await session.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )