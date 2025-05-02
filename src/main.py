from fastapi import FastAPI

from users.router import registration_router, auth_router, operation_user


app = FastAPI(
    title='Final project'
)

app.include_router(registration_router)
app.include_router(auth_router, tags=['Auth'])
app.include_router(operation_user)