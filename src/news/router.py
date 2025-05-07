from typing import Union, AsyncGenerator
from fastapi import APIRouter, Depends, status, Response

from database import get_session
from users.models import User
from users.schemas import UserInformation
from company.schemas.company import CompanyRead, CompanyCreate
from company.depencies import get_company_service
from company.service.company import CompanyService
from core_depencies import check_role
from news.schemas import NewsRead, NewsCreate
from news.depencies import get_news_service, check_company_news
from news.service import NewsService


news_router = APIRouter(
    prefix='/companies', tags=['News operations']
)

@news_router.post('/{company_id}/news', response_model=NewsRead)
async def create_news(
    company_id: int,
    data: NewsCreate,
    user: User = Depends(check_company_news),
    session: AsyncGenerator = Depends(get_session),
    service: NewsService = Depends(get_news_service)
) -> Union[NewsRead, Exception]:
    """
        Создаёт новость.

        Args:
            company_id (int): Идентификатор компании
            data (NewsCreate): Входные данные для создания новости.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (NewsService): Сервис для создания новости.
            
        Returns:
            NewsRead: Схема для отображения созданной новости.
    """

    news = await service.create_news(session, user, company_id, data)

    return NewsRead.model_validate(news)

@news_router.delete('/{company_id}/news/{news_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    company_id: int,
    news_id: int,
    user: User = Depends(check_company_news),
    session: AsyncGenerator = Depends(get_session),
    service: NewsService = Depends(get_news_service)
) -> None:
    """
        Удаляет новость.

        Args:
            company_id (int): Идентификатор компании
            news_id (int): Идентификатор новости.
            user (User): Получение текущего пользователя.
            session (AsyncGenerator): SQLAlchemy-сессия.
            service (NewsService): Сервис для создания новости.
    """

    await service.delete_news(session, user, company_id, news_id)