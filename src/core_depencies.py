from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users


#   проверка роли пользователя перез работой эндпоинтов
def check_role(user: User = Depends(fastapi_users.current_user())):
    if user.company_role != RoleType.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Только админ может использовать функционал оргструктуры'
        )
    
    return user

#   получение текущего авторизированного пользователя
def get_user(user: User = Depends(fastapi_users.current_user())):
    return user