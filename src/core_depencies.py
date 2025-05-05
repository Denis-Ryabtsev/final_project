from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from users.manager import fastapi_users


def check_role(
    user: User = Depends(fastapi_users.current_user())
):
    if user.company_role != RoleType.admin:
        print(f'\n\n\n{user.company_role}\n\n\n')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Только админ может использовать функционал оргструктуры'
        )
    
    return user

def get_user(
    user: User = Depends(fastapi_users.current_user())
):
    return user