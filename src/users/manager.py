from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.config_token import auth_backend
from config import get_setting
from database import get_session


setting = get_setting()

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = setting.SECRET
    verification_token_secret = setting.SECRET


async def get_user_db(session: AsyncSession = Depends(get_session)) -> AsyncGenerator:
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db = Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
