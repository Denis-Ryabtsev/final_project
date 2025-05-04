from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str
    description: str
    company_code: str = Field(min_length=4, max_length=4)
    admin_code: str = Field(min_length=6, max_length=6)


class CompanyRead(BaseModel):
    name: str
    description: str
    company_code: str

    model_config = {
        'from_attributes': True
    }