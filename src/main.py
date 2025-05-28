from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from users.router import registration_router, auth_user_router, operation_user
from company.router.company import company_router
from company.router.department import department_router
from news.router import news_router
from tasks.router.task import task_router
from tasks.router.comment import comment_router
from rating.router import rating_router
from meeting.router import meeting_router
from calendars.router import calendar_router
from database import db
from config import get_setting
from admin.setup import init_admin
from web.router import router as web_router
from database import get_setting


setting = get_setting()
BASE_DIR = setting.BASE_DIR
STATIC_DIR = setting.STATIC_DIR

app = FastAPI(title='Final project')

#   подключение статики
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

#   подключение html маршрутов
app.include_router(web_router)

#   подключение административного кабинета
init_admin(app, db.engine)

#   подключение роутеров API
app.include_router(registration_router)
app.include_router(auth_user_router, tags=['Auth'])
app.include_router(operation_user)
app.include_router(company_router)
app.include_router(department_router)
app.include_router(news_router)
app.include_router(task_router)
app.include_router(comment_router)
app.include_router(rating_router)
app.include_router(meeting_router)
app.include_router(calendar_router)
