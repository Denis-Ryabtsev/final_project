from typing import AsyncGenerator, Union

from fastapi import HTTPException, status
from sqlalchemy import select

from tasks.schemas.task import TaskChange, TaskCreate
from users.models import User
from tasks.models.task import Task, TaskStatus
from calendars.models import CalendarStatus, Calendar


class TaskService:
    """
        Сервисный слой для работы с задачами:
            - создание задачи
            - добавление задачи в календарь
            - удаление задачи
            - изменение данных задачи
            - изменение статуса задачи
    """

    async def create_task(
        self, user: User, session: AsyncGenerator, data: TaskCreate
    ) -> Union[dict, HTTPException]:
        """
            Создание новой задачи.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                data (TaskCreate): Входные данные для создания задачи

            Returns:
                task_data (dict): Словарь созданной задачи.
        """

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

            task_data = {
                'id': task.id,
                "owner_id": task.owner_id,
                "company_id": task.company_id,
                "target_id": task.target_id,
                "start_date": task.start_date,
                "end_date": task.end_date,
                "title": task.title,
                "description": task.description,
                "status": task.status,
            }

            return task_data

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def add_task_calendar(
        self, session: AsyncGenerator, task: Task
    ) -> Union[None, HTTPException]:
        """
            Добавление задачи в календарь пользователя.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                task (Task): Объект задачи.
        """

        try:
            calendar = {
                    'user_id': task['target_id'],
                    'event_date': task['end_date'],
                    'title': task['title'],
                    'type_event': CalendarStatus.task,
                    'task_id': task['id']
            }
            calendar = Calendar(**calendar)
            session.add(calendar)
            await session.commit()
            await session.refresh(calendar)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_task(
        self, user: User, task_id: int, session: AsyncGenerator
    ) -> Union[None, HTTPException]:
        """
            Удаление задачи.

            Args:
                user (User): Получение текущего пользователя.
                task_id (int): Идентификатор задачи
                session (AsyncGenerator): SQLAlchemy-сессия.
        """

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
        self, user: User, session: AsyncGenerator, data: TaskChange, task_id: int
    ) -> Union[Task, HTTPException]:
        """
            Изменение задачи.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                data (TaskChange): Входные данные для изменения задачи
                task_id (int): Идентификатор задачи

            Returns:
                target_task (Task): Объект задачи.
        """

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
        self, user: User, session: AsyncGenerator, task_id: int, task_status: TaskStatus
    ) -> Union[Task, HTTPException]:
        """
            Изменение статуса задачи.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                task_id (int): Идентификатор задачи
                task_status (TaskStatus): Тип статуса задачи

            Returns:
                target_task (Task): Объект задачи.
        """

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