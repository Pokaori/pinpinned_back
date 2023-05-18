from datetime import datetime

from pydantic import BaseModel
from pydantic.types import UUID4

from serialisers.comment import CommentOut
from serialisers.event import EventOut


class ScheduleOut(BaseModel):
    id: UUID4
    scheduled_at: datetime
    is_canceled: bool
    places_sub: int
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True


class ScheduleEventOut(ScheduleOut):
    event: EventOut
    comments: list[CommentOut]


class EventScheduleCreate(BaseModel):
    event_id: UUID4
    scheduled_at: datetime


class EventScheduleFilter(ScheduleEventOut):
    distance: float

    class Config:
        orm_mode = True
