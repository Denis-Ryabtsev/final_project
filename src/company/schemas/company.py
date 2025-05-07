from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """
        Схема для создания компании

        Fields:
        - name: Название компании.
        - description: Описание команды.
        - company_code: Код приглашения команды.
        - admin_code: Админ код для назначение роли админа.
    """

    name: str
    description: str
    company_code: str = Field(min_length=4, max_length=4)
    admin_code: str = Field(min_length=6, max_length=6)


class CompanyRead(BaseModel):
    """
        Схема для чтения компании

        Fields:
        - name: Название компании.
        - description: Описание команды.
        - company_code: Код приглашения команды.
    """

    name: str
    description: str
    company_code: str = Field(min_length=4, max_length=4)

    model_config = {
        'from_attributes': True
    }