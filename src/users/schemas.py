from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError

from users.models import RoleType


class UserRegistration(BaseModel):
    """
        Схема для получения данных при регистрации пользователей

        Fields:
        - first_name: Имя пользователя.
        - last_name: Фамилия пользователя.
        - company_role: Роль в компании.
        - company_code: Код компании для присоединения.
        - email: Почта пользователя.
        - password: Пароль от учетной записи.
  
    """

    first_name: str = Field(
        example='Иван', description='Введите свое имя', min_length=2, alias='name'
    )
    last_name: str = Field(
        example='Васильев', description='Введите свою фамилию', 
        min_length=2, alias='surname'
    )
    company_role: RoleType = Field(alias='role')
    company_code: Optional[str] = Field(
        None, example='aaaa', description='Введите код компании', 
        min_length=4, max_length=4, alias='code'
    )
    email: EmailStr = Field(
        example='user@mail.ru'
    )
    password: str = Field(
        description='Пароль должен состоять минимум из 6 символов', min_length=6
    )

    @field_validator('password')
    @classmethod
    def check_passwd(cls, value):
        if not (any(item.isdigit()) for item in value):
            raise ValidationError('В пароле нет цифр')
        
        return value


class UserCreate(schemas.BaseUserCreate):
    """
        Схема для регистрации пользователей в fastapi_users
    
        Fields:
        - first_name: Имя пользователя.
        - last_name: Фамилия пользователя.
        - company_role: Роль в компании.
        - company_id: Идентификатор компании.
        - department_id: Идентификатор отдела.
        - email: Почта пользователя.
        - password: Пароль от учетной записи.

    """

    first_name: str
    last_name: str
    company_role: RoleType
    company_id: Optional[int] = None
    department_id: Optional[int] = None
    email: EmailStr
    password: str 


class MessageResponse(BaseModel):
    """
        Схема для вывода сообщения при выполнении эндпоинта
        
        Fields:
        - message: Сообщение ответа.

    """
    message: str


class UserInformation(BaseModel):
    """
        Схема для вывода информации пользователе

        Fields:
        - first_name: Имя пользователя.
        - last_name: Фамилия пользователя.
        - company_role: Роль в компании.
        - company_id: Идентификатор компании.
        - department_id: Идентификатор отдела.

    """

    first_name: str
    last_name: str
    company_role: RoleType
    company_id: Optional[int] = None
    department_id: Optional[int] = None

    model_config = {
        'from_attributes': True
    }


class UserChange(BaseModel):
    """
        Схема для изменения данных пользователя

        Fields:
        - first_name: Имя пользователя.
        - last_name: Фамилия пользователя.
        - company_role: Роль в компании.
        - email: Почта пользователя.
        - company_code: Код компании для присоединения.

    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_role: Optional[RoleType] = None
    email: Optional[EmailStr] = None
    company_code: Optional[str] = None
