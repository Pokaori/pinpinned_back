from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import functions, Geography
from sqlalchemy import type_coerce, column, values, String, text
from sqlalchemy.future import select
from starlette import status

from models import User, Tag
from models.event import Event
from models.event_schedule import EventSchedule
from serialisers.event import EventCreate, EventOut, EventScheduleCreate, EventScheduleOut, EventScheduleFilter
from settings.auth import get_current_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', summary="Create event", response_model=EventOut)
async def create_event(data: EventCreate, session: Annotated[Any, Depends(get_async_session)],
                       user: Annotated[User, Depends(get_current_user)]):
    event_dict = data.dict()
    del event_dict["longitude"]
    del event_dict["latitude"]
    del event_dict["tags"]
    event_dict["author"] = user
    event_dict["place"] = data.place
    event = Event(**event_dict)
    new_tags = (await session.execute(
        select(values(column('name', String), name="my_tag").data((tag,) for tag in data.tags)).join(
            Tag, text("my_tag.name = tag.name"), isouter=True).where(Tag.name.is_(None)))).scalars().all()
    tags = [Tag(name=tag) for tag in new_tags]
    if tags:
        session.add_all(tags)
    event.tags = (await session.scalars(select(Tag).where(Tag.name.in_(data.tags)))).all()
    session.add(event)
    await session.commit()
    return event


@router.get("/{event_id}", dependencies=[Depends(get_current_user)], response_model=EventOut)
async def read_event(event_id: UUID, session: Annotated[Any, Depends(get_async_session)]):
    q = await session.get(Event, event_id)
    await session.commit()
    return q


@router.post('/{event_id}/schedule', summary='Create event schedule',
             response_model=EventScheduleOut)
async def create_schedule_event(event_id: UUID, data: EventScheduleCreate,
                                session: Annotated[Any, Depends(get_async_session)],
                                user: Annotated[User, Depends(get_current_user)]):
    event = await session.get(Event, event_id)
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
async def find_events(session: Annotated[Any, Depends(get_async_session)], latitude: float, longitude: float,
                      distance: int, scheduled_lte: datetime | None = None, scheduled_gte: datetime | None = None,
                      fee: float | None = None):
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
    query.order_by("distance", EventSchedule.scheduled_at)
    res = (await session.execute(query)).all()
    return [EventScheduleFilter(**EventScheduleOut.from_orm(filter[0]).dict(), distance=filter[2] / 1000) for filter in
            res]
