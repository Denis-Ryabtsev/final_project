from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.models import User
from news.schemas import NewsRead, NewsCreate
from news.depencies import get_news_service, check_company_news
from news.service import NewsService


news_router = APIRouter(
    prefix='/companies', tags=['News']
)

@news_router.post('/{company_id}/news', response_model=NewsRead)
async def create_news(
    company_id: int,
    data: NewsCreate,
    user: User = Depends(check_company_news),
    session: AsyncSession = Depends(get_session),
    service: NewsService = Depends(get_news_service)
) -> Union[NewsRead, Exception]:
    """
        Создание новости.

        Args:
            company_id (int): Идентификатор компании
            data (NewsCreate): Входные данные для создания новости.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (NewsService): Сервис для создания новости.
            
        Returns:
            NewsRead: Схема для отображения созданной новости.
    """

    news = await service.create_news(session, user, company_id, data)

    return NewsRead.model_validate(news)

@news_router.delete('/{company_id}/news/{news_id}', status_code=204)
async def delete_news(
    company_id: int,
    news_id: int,
    user: User = Depends(check_company_news),
    session: AsyncSession = Depends(get_session),
    service: NewsService = Depends(get_news_service)
) -> None:
    """
        Удаление новости.

        Args:
            company_id (int): Идентификатор компании
            news_id (int): Идентификатор новости.
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (NewsService): Сервис для создания новости.
    """

    await service.delete_news(session, user, company_id, news_id)

@news_router.get('/{company_id}/news', response_model=list[NewsRead])
async def get_news(
    company_id: int,
    user: User = Depends(check_company_news),
    session: AsyncSession = Depends(get_session),
    service: NewsService = Depends(get_news_service)
) -> list[NewsRead]:
    """
        Получение новости.

        Args:
            company_id (int): Идентификатор компании
            user (User): Получение текущего пользователя.
            session (AsyncSession): SQLAlchemy-сессия.
            service (NewsService): Сервис для создания новости.
        
        Returns:
            company_news (list[NewsRead]): Список новостей.
    """

    company_news = await service.get_news(session, company_id)

    return NewsRead.model_validate(company_news)