from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.future import select

from models import Tag
from serialisers.tag import TagOut
from settings.auth import get_current_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", dependencies=[Depends(get_current_user)], response_model=list[TagOut])
async def get_tags(session: Annotated[Any, Depends(get_async_session)]):
    q = await session.execute(select(Tag).order_by(desc(Tag.event_count), Tag.name))
    return q.scalars().unique().all()
