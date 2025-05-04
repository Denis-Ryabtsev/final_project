from fastapi import Depends, HTTPException, status
from core_depencies import check_role
from users.models import User
from news.service import NewsService


def check_company_news(user: User = Depends(check_role)):
    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Новости можно выставлять только при наличии команды'
        )
    
    return user

def get_news_service() -> NewsService:
    return NewsService()