from typing import Union

from fastapi import Depends, HTTPException, status

from users.models import User
from core_depencies import check_role
from tasks.service.task import TaskService
from tasks.service.comment import CommentService


#   проверка принадлежности к команде
def check_company(user: User = Depends(check_role)) -> Union[User, HTTPException]:
    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нужно наличие компании'
        )
    
    return user

#   возврат объекта сервиса для задачи
def get_task_service() -> TaskService:
    return TaskService()

#   возврат объекта сервиса для комментариев
def get_comment_service() -> CommentService:
    return CommentService()