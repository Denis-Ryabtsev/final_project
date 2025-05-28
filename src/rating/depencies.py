from typing import Union

from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from core_depencies import get_user
from rating.service import RatingService


#   получение объекта сервиса для оценки
def get_rating_service() -> RatingService:
    return RatingService()

#   проверка роли пользователя в команде
def check_rating_role(user: User = Depends(get_user)) -> Union[User, HTTPException]:
    if user == RoleType.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Оценивать может только админ или менеджер'
        )
    
    return user