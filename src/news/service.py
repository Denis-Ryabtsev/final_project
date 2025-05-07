from typing import AsyncGenerator, Union

from fastapi import HTTPException, status, Depends
from sqlalchemy import select

from users.models import User
from news.models import News
from news.schemas import NewsCreate



class NewsService:
    
    async def create_news(
        self, session: AsyncGenerator, user: User, company_id: int, data: NewsCreate
    ) -> Union[News, HTTPException]:
        """
            Создание новости.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                company_id (int): Идентификатор компании
                data (NewsCreate): Входные данные для создания новости

            Returns:
                data (News): Объект новости.
        """

        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Новости можно выставлять только в компании, к которой прикреплен'
            )
        
        data = {
            'owner_id': user.id,
            'company_id': user.company_id,
            'title': data.title,
            'description': data.description
        }
        data = News(**data)

        try:
            session.add(data)
            await session.commit()
            await session.refresh(data)

            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_news(
        self, session: AsyncGenerator, user: User, company_id: int, news_id: int
    ) -> Union[None, HTTPException]:
        """
            Удаление новости.

            Args:
                session (AsyncGenerator): SQLAlchemy-сессия.
                user (User): Получение текущего пользователя.
                company_id (int): Идентификатор компании
                news_id (int): Идентификатор новости
        """

        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Новости можно удалять только в компании, к которой прикреплен'
            )
        query = select(News).where(News.id == news_id)
        target_news = (await session.execute(query)).scalars().first()
        if not target_news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Новости с id {news_id} не существует'
            )
        
        try:
            await session.delete(target_news)
            await session.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )