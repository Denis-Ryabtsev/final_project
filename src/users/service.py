from typing import AsyncGenerator

from fastapi import HTTPException, status
from fastapi_users.exceptions import UserAlreadyExists

from users.schemas import UserCreate, UserChange
from users.models import User


class UserService:
    def __init__(self, user_manager):
        self.user_manager = user_manager

    async def register_user(self, data: UserCreate):
        try:
            await self.user_manager.create(data)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Пользователь {data.email} уже существует'
            )
        
    async def get_user(self, user: User):
        return user
    
    async def change_user(self, session: AsyncGenerator, user: User, data: UserChange) -> User:
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