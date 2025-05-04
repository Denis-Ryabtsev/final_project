from pydantic import BaseModel, Field


class DepartmentRead(BaseModel):
    name: str
    company_id: int
    head_user_id: int

    model_config = {
        'from_attributes': True
    }


class DepartmentCreate(BaseModel):
    name: str
    head_user_id: int
