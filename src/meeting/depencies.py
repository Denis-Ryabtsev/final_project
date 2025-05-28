from fastapi import Depends, HTTPException, status

from users.models import User, RoleType
from core_depencies import get_user
from meeting.service import MeetingService


#   проверка на роль и наличие команды
def check_company_role_meeting(user: User = Depends(get_user)):
    if user == RoleType.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Создавать встречи может только менеджер или админ'
        )
    elif not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Чтобы создавать встречи, нужно находится в команде'
        )
    
    return user

#   возврат объекта сервиса для встреч
def get_meeting_service() -> MeetingService:
    return MeetingService()