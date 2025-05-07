from pydantic import BaseModel


class DepartmentRead(BaseModel):
    """
        Схема для получения данных об отделе

        Fields:
        - name: Название отдела.
        - company_id: Идентификатор компании.
        - head_user_id: Руководитель отдела.
    """

    name: str
    company_id: int
    head_user_id: int

    model_config = {
        'from_attributes': True
    }


class DepartmentCreate(BaseModel):
    """
        Схема для создания отдела

        Fields:
        - name: Название отдела.
        - head_user_id: Руководитель отдела.
    """
    
    name: str
    head_user_id: int
