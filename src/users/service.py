from datetime import datetime
from typing import AsyncGenerator, Union

from fastapi import HTTPException, status
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from rating.schemas import AvgRatingRead
from users.schemas import UserCreate, UserChange, UserRegistration
from users.models import RoleType, User
from company.models.company import Company
from rating.models import Rating


class UserService:
    """
        Сервисный слой для работы с пользователями:
            - создание пользователей
            - получение информации о пользователе
            - редактирование профиля пользователя
            - удаления пользователя
            - изменение роли пользователя админом
            - удаления пользователя из отдела
            - получение оценок задач
            - получение средних значений оценок задач
    """

    def __init__(self, user_manager):
        self.user_manager = user_manager

    async def register_user(
        self, session: AsyncGenerator, data: UserRegistration
    ) -> Union[None, UserAlreadyExists, HTTPException]:
        """
            Создаёт нового пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                data (UserRegistration): Входные данные для регистрации пользователя.
            
        """

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
        
    async def get_user(self, user: User) -> User:
        """
            Получение данных пользователя.

            Args:
                user (User): Получение текущего пользователя.

            Returns:
                user (User): Получение текущего пользователя.
        """

        return user
    
    async def change_user(
        self, session: AsyncGenerator, user: User, data: UserChange
    ) -> Union[User, HTTPException]:
        """
            Изменение данных пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                data (UserChange): Входные данные для изменения данных пользователя

            Returns:
                user (User): Получение текущего пользователя.
            
        """

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

        await session.commit()
        await session.refresh(user)

        return user
    
    async def delete_user(self, session: AsyncGenerator, user: User) -> None:
        """
            Удаление пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
            
        """

        await session.delete(user)
        await session.commit()

    async def change_role(
        self, session: AsyncGenerator, user: User, user_id: int, role: RoleType
    ) -> Union[User, HTTPException]:
        """
            Изменение роли пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                user_id (int): Идентификатор пользователя.
                role (RoleType): Тип роли в команде

            Returns:
                target_user (User): Получение текущего пользователя.
            
        """

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
        await session.commit()
        await session.refresh(target_user)

        return target_user
    
    async def delete_department(
        self, session: AsyncGenerator, user: User, user_id: int
    ) -> Union[User, HTTPException]:
        """
            Удаление пользователя из отдела.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                user_id (int): Идентификатор пользователя.

            Returns:
                target_user (User): Получение текущего пользователя.
            
        """

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
        await session.commit()
        await session.refresh(target_user)

        return target_user
    
    async def get_rating(self, session: AsyncGenerator, user: User) -> list[Rating]:
        """
            Получение оценок задач пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.

            Returns:
                list (Rating): Получение оценок задач пользователя.
            
        """

        query = (
            select(Rating)
            .options(selectinload(Rating.evaluator), selectinload(Rating.task))
            .where(Rating.owner_id == user.id)
        )
        result = await session.execute(query)

        return result.scalars().all()
    
    async def get_avg_rating(
        self, session: AsyncGenerator, user: User
    ) -> AvgRatingRead:
        """
            Получение средних оценок задач пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.

            Returns:
                (AvgRatingRead): Схема средних значений оценок задач пользователя.
            
        """

        today = datetime.utcnow().date()
        quarter = (today.month - 1) // 3 + 1
        quarter_start_month = 3 * (quarter - 1) + 1
        quarter_start = datetime(today.year, quarter_start_month, 1).date()

        query = (
            select(
                func.avg(Rating.score_date).label("avg_date"),
                func.avg(Rating.score_quality).label("avg_quality"),
                func.avg(Rating.score_complete).label("avg_complete"),
            )
            .where(
                Rating.owner_id == user.id,
                Rating.created_at >= quarter_start,
            )
        )

        result = await session.execute(query)
        row = result.mappings().first() or {}
        return AvgRatingRead(**row)