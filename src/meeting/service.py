import datetime
from typing import AsyncGenerator

from fastapi import HTTPException, status, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from users.schemas import UserInformation
from tasks.schemas.task import TaskChange
from users.models import User
from company.schemas.department import DepartmentCreate
from company.models.department import Department
from tasks.models.task import Task, TaskStatus
from rating.models import Rating
from rating.schemas import AvgRatingRead
from meeting.schemas import MeetingCreate, MeetingChange
from meeting.models import Meeting
from calendars.models import Calendar, CalendarStatus
# from company.depencies import check_role


class MeetingService:
    async def create_meeting(
        self, user: User, session: AsyncGenerator, data: MeetingCreate
    ):
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
    ):
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
    ):
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
        self, user: User, session: AsyncGenerator, meeting_id: int, user_id
    ):
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
    #     query = (
    # select(User)
    # .options(selectinload(User.department), selectinload(User.company))
    # .where(User.id == user_id)
# )
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

            # return data
            # return UserInformation.model_validate(add_user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )