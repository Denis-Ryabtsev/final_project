from typing import AsyncGenerator, Union

from fastapi import HTTPException, status
from sqlalchemy import select

from users.models import User
from meeting.schemas import MeetingCreate, MeetingChange
from meeting.models import Meeting
from calendars.models import Calendar, CalendarStatus


class MeetingService:
    """
        Сервисный слой для работы со встречами:
            - создание встреч
            - удаление встреч
            - изменение встреч
            - добавление пользователей на встречу
    """

    async def create_meeting(
        self, user: User, session: AsyncGenerator, data: MeetingCreate
    ) -> Union[Meeting, HTTPException]:
        """
            Создаёт новую встречу.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                data (MeetingCreate): Входныеы данные для создания встречи

            Returns:
                target_meeting (Meeting): Объект встречи.
        """

        target_meeting = data.model_dump()
        target_meeting['organizer_id'] = user.id
        target_meeting['company_id'] = user.company_id

        try:
            target_meeting = Meeting(**target_meeting)
            session.add(target_meeting)
            await session.commit()
            await session.refresh(target_meeting)

            return target_meeting
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def delete_meeting(
        self, user: User, session: AsyncGenerator, meeting_id: int
    ) -> Union[None, HTTPException]:
        """
            Удаление встречи.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                meeting_id (int): Идентификатор встречи
        """

        query = select(Meeting).where(Meeting.id == meeting_id)
        target_meeting = (await session.execute(query)).scalars().first()
        if not target_meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Встреча с таким id {meeting_id} не существует'
            )
        if target_meeting.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Можно удалять встречи только своей компании'
            )

        try:
            await session.delete(target_meeting)
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def change_meeting(
        self, user: User, session: AsyncGenerator, meeting_id: int, data: MeetingChange
    ) -> Union[Meeting, HTTPException]:
        """
            Изменение встречи.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                meeting_id (int): Идентификатор встречи
                data (MeetingChange): Входные данные для изменения встречи
                
            Returns:
                target_meeting (Meeting): Объект встречи.
        """

        data = data.model_dump(exclude_unset=True)
        if not data.items():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Нет данных для изменения'
            )
        
        query = select(Meeting).where(Meeting.id == meeting_id)
        target_meeting = (await session.execute(query)).scalars().first()
        if not target_meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Встреча с таким id {meeting_id} не существует'
            )
        if target_meeting.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Можно изменять встречи только своей компании'
            )

        try:
            for k, v in data.items():
                setattr(target_meeting, k, v)

            await session.commit()
            await session.refresh(target_meeting)

            return target_meeting
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
    async def add_user_meeting(
        self, user: User, session: AsyncGenerator, meeting_id: int, user_id: int
    ) -> Union[None, HTTPException]:
        """
            Добавление пользователей на встречу.

            Args:
                user (User): Получение текущего пользователя.
                session (AsyncGenerator): SQLAlchemy-сессия.
                meeting_id (int): Идентификатор встречи
                user_id (int): Идентификатор пользователя
        """

        query = select(Meeting).where(Meeting.id == meeting_id)
        target_meeting = (await session.execute(query)).scalars().first()
        if not target_meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Встреча с таким id {meeting_id} не существует'
            )
        if target_meeting.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Можно изменять встречи только своей компании'
            )
        
        query = select(User).where(User.id == user_id)
        add_user = (await session.execute(query)).scalars().first()
        if not add_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с таким id {user_id} не существует'
            )
        if add_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Добавленные пользователи должны быть из твоей команды'
            )

        query = select(Calendar).where(
            Calendar.user_id == user_id, 
            Calendar.event_date == target_meeting.meeting_date,
            Calendar.event_time == target_meeting.meeting_time
        )
        busy_slot = (await session.execute(query)).scalars().first()
        if busy_slot:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'У пользователя на данный слот уже есть встреча'
            )

        try:
            data = {
                'user_id': user_id,
                'event_date': target_meeting.meeting_date,
                'event_time': target_meeting.meeting_time,
                'title': target_meeting.title,
                'type_event': CalendarStatus.meeting,
                'meeting_id': target_meeting.id
            }
            data = Calendar(**data)

            session.add(data)
            await session.commit()
            await session.refresh(data)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )