from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from serialisers.user import UserOut


class CommentCreate(BaseModel):
    schedule_id: UUID4
    text: str | None
    rating: int | None = Field(ge=0, le=5)


class CommentOut(BaseModel):
    id: UUID4
    text: str | None
    rating: int | None = Field(ge=0, le=5)
    user: UserOut
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    text: str | None
    rating: int | None = Field(ge=0, le=5)
