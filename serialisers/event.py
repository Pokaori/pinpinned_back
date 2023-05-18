import json
from datetime import datetime
from typing import Any

from geoalchemy2 import functions
from pydantic import BaseModel, UUID4, Field, validator, constr

from serialisers.tag import TagOut
from serialisers.user import UserOut
from settings.db import get_session

TagValidate = constr(regex=r"[\w_-]+")


class EventCreate(BaseModel):
    title: str = Field(max_length=100)
    description: str
    duration: int = Field(lt=25, gt=0)
    fee: float | None = Field(gt=0)
    longitude: float
    latitude: float
    tags: list[TagValidate]

    @property
    def place(self):
        return f"POINT({self.latitude} {self.longitude})"


class EventOut(BaseModel):
    id: UUID4
    title: str = Field(max_length=100)
    description: str
    duration: int = Field(lt=25, gt=0)
    fee: float | None = Field(ge=0)
    author: UserOut
    place: Any
    tags: list[TagOut]
    created_at: datetime | None
    updated_at: datetime | None

    @validator("place")
    def place_to_dict(cls, v):
        if isinstance(v, dict):
            return v
        session = get_session()
        place = json.loads(session.execute(functions.ST_AsGeoJSON(v)).scalars().first())
        res = {"latitude": place["coordinates"][0], "longitude": place["coordinates"][1]}
        return res

    class Config:
        orm_mode = True


class ScheduleOut(BaseModel):
    id: UUID4
    scheduled_at: datetime
    is_canceled: bool
    places_sub: int
    created_at: datetime | None
    updated_at: datetime | None
    class Config:
        orm_mode = True


class EventScheduleOut(EventOut):
    schedules: list[ScheduleOut]
