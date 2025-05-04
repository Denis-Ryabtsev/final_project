from typing import AsyncGenerator

from fastapi import HTTPException, status
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select

from users.schemas import UserCreate, UserChange, UserRegistration
from company.models.department import Department
from users.models import RoleType, User
from company.models.company import Company


class UserService:
    def __init__(self, user_manager):
        self.user_manager = user_manager

    async def register_user(self, session: AsyncGenerator, data: UserRegistration):
        if data.company_code:
            query = select(Company.id).where(Company.company_code == data.company_code)
            result = (await session.execute(query)).scalars().first()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Компания с кодом {data.company_code} не найдена'
                )
            data = data.model_dump(exclude={'company_code'})
            data['company_id'] = result
        else:
            data = data.model_dump()
        
        try:
            await self.user_manager.create(UserCreate(**data))
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Пользователь {data['email']} уже существует'
            )
        
    async def get_user(self, user: User):
        return user
    
    async def change_user(self, session: AsyncGenerator, user: User, data: UserChange) -> User:
        if data.company_code:
            query = select(Company.id).where(Company.company_code == data.company_code)
            result = (await session.execute(query)).scalars().first()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Компания с кодом {data.company_code} не найдена'
                )
            data = data.model_dump(exclude={'company_code'}, exclude_unset=True)
            data['company_id'] = result
        else:
            data = data.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нет данных для изменения'
            )
        
        for k, v in data.items():
            setattr(user, k, v)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    async def delete_user(self, session: AsyncGenerator, user: User):
        await session.delete(user)
        await session.commit()

    async def change_role(self, session: AsyncGenerator, user: User, user_id: int, role: RoleType):
        target_user = await session.get(User, user_id)
        if not user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Ты должен находиться в команде'
            )
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не существует'
            )
        
        if target_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь с id {target_user.company_id} должен быть из твоей команды'
            )
        
        target_user.company_role = role
        session.add(target_user)
        await session.commit()
        await session.refresh(target_user)

        return target_user
    
    async def delete_department(self, session: AsyncGenerator, user: User, user_id: int):
        target_user = await session.get(User, user_id)
        if not user.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Ты должен находиться в команде'
            )
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не существует'
            )
        
        if target_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь с id {target_user.company_id} должен быть из твоей команды'
            )
        
        if not target_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь с id {target_user.company_id} не состоит в команде'
            )
        
        target_user.department_id = None
        session.add(target_user)
        await session.commit()
        await session.refresh(target_user)

        return target_user
