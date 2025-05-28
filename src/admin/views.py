from sqladmin import ModelView

from users.models import User
from company.models.company import Company
from tasks.models.task import Task


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.first_name, User.last_name, User.company_role]


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name, Company.company_code]


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.title, Task.status, Task.owner_id, Task.target_id]