from sqladmin import Admin
from .auth import AdminAuth
from .views import UserAdmin, CompanyAdmin, TaskAdmin
from config import get_setting


setting = get_setting()

def init_admin(app, engine):
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=setting.SECRET_ADMIN))
    admin.add_view(UserAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(TaskAdmin)