from typing import AsyncGenerator, Union

from fastapi import HTTPException, status
from sqlalchemy import select

from users.models import User
from company.schemas.company import CompanyCreate, CompanyRead
from company.models.company import Company


class CompanyService:
    """
        Сервисный слой для работы с компанией:
            - создание компании
            - добавление пользователей в компанию
            - удаление пользователей из команды
            - удаления компании
    """

    async def create_company(
        self, session: AsyncGenerator, data: CompanyCreate
    ) -> Union[Company, HTTPException]:
        """
            Создание компании.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                data (CompanyCreate): Входные данные для создания компании.

            Returns:
                (CompanyRead): Схема для отображения данных компании.
        """

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
    ) -> Union[User, HTTPException]:
        """
            Добавление пользователей.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                company_id (int): Идентификатор компании
                user_id (int): Идентификатор пользователя

            Returns:
                user (User): Объект пользователя.
        """

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
    ) -> Union[User, HTTPException]:
        """
            Удаление пользователей из компании.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                company_id (int): Идентификатор компании
                user_id (int): Идентификатор пользователя

            Returns:
                user (User): Объект пользователя.
        """

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
    ) -> Union[None, HTTPException]:
        """
            Удаление компании.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                company_id (int): Идентификатор компании
        """

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