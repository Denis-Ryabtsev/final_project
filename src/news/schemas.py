from pydantic import BaseModel


class NewsCreate(BaseModel):
    title: str
    description: str


class NewsRead(BaseModel):
    owner_id: int
    company_id: int
    title: str
    description: str

    model_config = {
        'from_attributes': True
    }