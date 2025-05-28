from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from company.schemas.department import DepartmentCreate
from company.models.department import Department


class DepartmentService:
    """
        Сервисный слой для работы с отделами:
            - создание отделов
            - смена руководителя отдела
            - удаление отдела
    """

    async def create_department(
        self, session: AsyncSession, user: User, company_id: int, data: DepartmentCreate
    ) -> Union[Department, HTTPException]:
        """
            Создание отделов.

            Args:
                session (AsyncSession): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                company_id (int): Идентификатор компании
                data (DepartmentCreate): Входные данные для создания отделов

            Returns:
                new_department (Department): Объект отдела.
        """

        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Создавать отделы можно только в той команде, к которой ты прикреплен'
            )
        query = select(Department).where(Department.name == data.name)
        target_department = (await session.execute(query)).scalars().first()
        if target_department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Такой отдел {data.name} уже существует'
            )

        query = select(User).where(User.id == data.head_user_id)
        target_user = (await session.execute(query)).scalars().first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователя с таким id {data.head_user_id} не существует'
            )
        if target_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь не из твоей команды'
            )

        try:
            data = {
                'name': data.name,
                'company_id': company_id,
                'head_user_id': data.head_user_id
            }
            new_department = Department(**data)
            
            session.add(new_department)
            await session.commit()
            await session.refresh(new_department)
            target_user.department_id = new_department.id
            await session.commit()
            await session.refresh(new_department)

            return new_department
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def change_head_user(
        self, session: AsyncSession, user: User, 
        company_id: int, department_id: int, user_id: int
    ) -> Union[Department, HTTPException]:
        """
            Смена руководителя отдела.

            Args:
                session (AsyncSession): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                company_id (int): Идентификатор компании
                department_id (int): Идентификатор отдела
                user_id (int): Идентификатор пользователя

            Returns:
                target_department (Department): Объект отдела.
        """

        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Изменять отделы можно только в той команде, к которой ты прикреплен'
            )
        query = select(Department).where(Department.id == department_id)
        target_department = (await session.execute(query)).scalars().first()
        if not target_department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Такого отдела {department_id} не существует'
            )

        query = select(User).where(User.id == user_id)
        target_user = (await session.execute(query)).scalars().first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователя с таким id {user_id} не существует'
            )
        if target_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь не из твоей команды'
            )

        try:
            query = select(User).where(User.id == target_department.head_user_id)
            old_user = (await session.execute(query)).scalars().first()
            
            target_department.head_user_id = target_user.id
            target_user.department_id = target_department.id

            if old_user:
                old_user.department_id = None

            await session.commit()

            await session.refresh(target_department)
            await session.refresh(target_user)
            if old_user:
                await session.refresh(old_user)

            return target_department

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_department(
        self, session: AsyncSession, user: User, 
        company_id: int, department_id: int
    ) -> Union[None, HTTPException]:
        """
            Удаление отдела.

            Args:
                session (AsyncSession): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                company_id (int): Идентификатор компании
                department_id (int): Идентификатор отдела
        """

        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Изменять отделы можно только в той команде, к которой ты прикреплен'
            )
        query = select(Department).where(Department.id == department_id)
        target_department = (await session.execute(query)).scalars().first()
        if not target_department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Такого отдела {department_id} не существует'
            )
        
        try:
            query_users = select(User).where(User.department_id == department_id)
            users_to_update = (await session.execute(query_users)).scalars().all()

            for user in users_to_update:
                user.department_id = None
            await session.delete(target_department)
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )