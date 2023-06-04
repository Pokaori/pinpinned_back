from datetime import datetime

from pydantic import Field, BaseModel
from pydantic import UUID4

from serialisers.schedule import ScheduleEventOut
from serialisers.user import UserOut


class SubscriptionCreate(BaseModel):
    schedule_id: UUID4
    people_number: int = Field(gt=0, le=10)


class SubscriptionOut(BaseModel):
    id: UUID4
    people_number: int = Field(gt=0, le=10)
    schedule: ScheduleEventOut
    user: UserOut
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True

class SubscriptionGet(BaseModel):
    schedule_id: UUID4