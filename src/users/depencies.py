from fastapi import Depends
from users.manager import get_user_manager
from users.service import UserService


def get_user_service(user_manager = Depends(get_user_manager)) -> UserService:
    return UserService(user_manager)