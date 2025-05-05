from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from tasks.schemas.task import TaskChange
from users.models import User
from company.schemas.department import DepartmentCreate
from company.models.department import Department
from tasks.models.task import Task
# from company.depencies import check_role


class TaskService:
    async def create_task(
        self, user, session, data
    ):
        query = select(User).where(User.id == data.target_id)
        target_user = (await session.execute(query)).scalars().first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователя с таким id {data.target_id} не существует'
            )
        if target_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Пользователь не из твоей команды'
            )
        
        try:
            task = {
                'owner_id': user.id,
                'company_id': user.company_id,
                'target_id': target_user.id,
                'start_date': data.start_date,
                'end_date': data.end_date,
                'title': data.title,
                'description': data.description
            }
            task = Task(**task)
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return task

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def delete_task(
        self, user, task_id, session
    ):
        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задачи с таким id {task_id} не существует'
            )
        if target_task.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Задача не из твоей команды'
            )
        
        try:
            await session.delete(target_task)
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def change_task(
        self, user, session, data: TaskChange, task_id
    ):
        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задачи с таким id {task_id} не существует'
            )
        if target_task.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Задача не из твоей команды'
            )
        try:
            task = data.model_dump(exclude_unset=True)
            for k, v in task.items():
                setattr(target_task, k, v)

            await session.commit()
            await session.refresh(target_task)

            return target_task

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def change_task_role(
        self, user, session, task_id, task_status
    ):
        query = select(Task).where(Task.id == task_id)
        target_task = (await session.execute(query)).scalars().first()
        if not target_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задачи с таким id {task_id} не существует'
            )
        if target_task.target_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Можно менять статус только своих задач'
            )
        try:
            target_task.status = task_status.status
            await session.commit()
            await session.refresh(target_task)

            return target_task

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )