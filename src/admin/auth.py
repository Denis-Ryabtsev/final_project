from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from config import get_setting


# setting = get_setting()


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.middlewares = [
            (SessionMiddleware, {"secret_key": self.secret_key}, {})
        ]

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == "admin" and password == "admin":
            request.session["token"] = self.secret_key
            return True
        return False

    async def logout(self, request: Request) -> Response:
        request.session.clear()
        return RedirectResponse(url="/admin/login", status_code=302)

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == self.secret_key