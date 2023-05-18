from pydantic import BaseModel, Field


class TagOut(BaseModel):
    name: str = Field(regex=r"[\w_-]+", max_length=20)
    event_count: int

    class Config:
        orm_mode = True
