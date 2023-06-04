from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import column, values, String, text
from sqlalchemy.future import select
from models import User, Tag
from models.event import Event
from serialisers.event import EventCreate, EventOut, EventScheduleOut
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
    old_tags = list(set(data.tags) - set(new_tags))
    old_tags = (await session.scalars(select(Tag).where(Tag.name.in_(old_tags)))).unique().all()
    event.tags = tags + old_tags
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.get('/my', summary='Find my events', response_model=list[EventScheduleOut])
async def get_my_event(session: Annotated[Any, Depends(get_async_session)],
                       user: Annotated[User, Depends(get_current_user)]):
    events = (await session.execute(select(Event).where(Event.author_id == user.id))).scalars().unique().all()
    return events


@router.get("/{event_id}", dependencies=[Depends(get_current_user)], response_model=EventOut)
async def read_event(event_id: UUID, session: Annotated[Any, Depends(get_async_session)]):
    q = await session.get(Event, event_id)
    return q
