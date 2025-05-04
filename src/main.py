from fastapi import FastAPI

from users.router import registration_router, auth_router, operation_user
from company.router.company import company_router
from company.router.department import department_router
from news.router import news_router


app = FastAPI(
    title='Final project'
)

app.include_router(registration_router)
app.include_router(auth_router, tags=['Auth'])
app.include_router(operation_user)
app.include_router(company_router)
app.include_router(department_router)
app.include_router(news_router)