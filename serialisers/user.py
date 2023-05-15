from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, UUID4, validator
from models.user import GenderChoices


class UserAuth(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: str
    date_of_birth: date
    gender: GenderChoices = GenderChoices.UNDEFINED


class UserOut(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Any
    date_of_birth: date
    gender: GenderChoices = GenderChoices.UNDEFINED
    created_at: datetime | None
    updated_at: datetime | None

    @validator("phone_number")
    def phone_number_to_str(cls, v):
        return v if isinstance(v, str) else v.e164

    class Config:
        orm_mode = True
        use_enum_values = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenSchemaAccess(BaseModel):
    access_token: str


class TokenPayload(BaseModel):
    sub: str
    exp: float
