from pydantic import BaseModel


class CommentCreate(BaseModel):
    description: str


class CommentRead(BaseModel):
    author_id: int
    task_id: int
    description: str

    model_config = {
        'from_attributes': True
    }