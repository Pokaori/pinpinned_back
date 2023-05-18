from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import functions, Geography
from sqlalchemy import type_coerce
from sqlalchemy.future import select
from starlette import status

from models.event_schedule import EventSchedule
from models.event import Event
from models.user import User
from serialisers.schedule import EventScheduleCreate, ScheduleEventOut, EventScheduleFilter
from settings.auth import get_current_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', summary='Create event schedule', response_model=ScheduleEventOut)
async def create_schedule_event(data: EventScheduleCreate, session: Annotated[Any, Depends(get_async_session)],
                                user: Annotated[User, Depends(get_current_user)]):
    event = await session.get(Event, data.event_id)
    if event.author != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not owner of this event"
        )
    event_schedule = EventSchedule(**data.dict(), event=event)
    session.add(event_schedule)
    await session.commit()
    await session.refresh(event_schedule)
    return event_schedule


@router.get("/", dependencies=[Depends(get_current_user)], response_model=list[EventScheduleFilter])
async def find_schedules(session: Annotated[Any, Depends(get_async_session)], latitude: float, longitude: float,
                         distance: int, scheduled_lte: datetime | None = None, scheduled_gte: datetime | None = None,
                         fee: float | None = None, tags: list[str] | None = None):
    query = select(EventSchedule, Event,
                   functions.ST_Distance(Event.place, type_coerce(f"Point({latitude} {longitude})", Geography)).label(
                       'distance')).join_from(EventSchedule, Event).filter(
        functions.ST_DWithin(Event.place, type_coerce(f"Point({latitude} {longitude})", Geography), distance * 1000))
    if scheduled_lte is not None:
        query = query.filter(EventSchedule.scheduled_at <= scheduled_lte)
    if scheduled_gte is not None:
        query = query.filter(EventSchedule.scheduled_at >= scheduled_gte)
    if fee is not None:
        query = query.filter(Event.fee <= fee)
    if len(tags) > 0:
        query = query.filter(Event.tags.in_(tags))
    query.order_by("distance", EventSchedule.scheduled_at)
    res = (await session.execute(query)).all()
    return [EventScheduleFilter(**ScheduleEventOut.from_orm(filter[0]).dict(), distance=filter[2] / 1000) for filter in
            res]


@router.get('/user', summary='Find user schedules', dependencies=[Depends(get_current_user)],
            response_model=list[ScheduleEventOut])
async def get_user_schedules(session: Annotated[Any, Depends(get_async_session)], user_id: UUID):
    schedules = (await session.scalars(
        select(EventSchedule).join_from(EventSchedule, Event).where(Event.author_id == user_id))).all()
    return schedules


@router.post("/{schedule_id}/cancel", response_model=ScheduleEventOut)
async def cancel_schedule(schedule_id: UUID, session: Annotated[Any, Depends(get_async_session)],
                          user: Annotated[User, Depends(get_current_user)]):
    schedule = await session.get(EventSchedule, schedule_id)
    if schedule.event.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not owner of this schedule"
        )
    schedule.is_canceled = True
    await session.commit()
    return schedule
