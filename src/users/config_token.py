from fastapi_users.authentication import (
    CookieTransport, JWTStrategy, AuthenticationBackend
)

from config import get_setting


setting = get_setting()

cookie_transport = CookieTransport(cookie_name='project', cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=setting.SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name='jwt_access',
    transport=cookie_transport,
    get_strategy=get_jwt_strategy
)
