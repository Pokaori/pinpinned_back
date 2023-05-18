from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

import pytz
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from starlette import status

from models import Subscription
from models.comment import Comment
from models.event_schedule import EventSchedule
from models.user import User
from serialisers.comment import CommentOut, CommentCreate, CommentUpdate
from settings.auth import get_current_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/comment",
    tags=["comment"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', summary='Create comment', response_model=CommentOut)
async def create_comment(data: CommentCreate, session: Annotated[Any, Depends(get_async_session)],
                         user: Annotated[User, Depends(get_current_user)]):
    schedule = (await session.execute(select(EventSchedule).where(EventSchedule.id == data.schedule_id))).scalars().first()
    comment = (await session.scalars(
        select(Comment).where(Comment.schedule_id == data.schedule_id).where(Comment.user_id == user.id))).first()
    if schedule.event.author_id != user.id and comment is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have comment.")
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event doesn't exist.")
    if data.rating is not None and schedule.scheduled_at > datetime.now(tz=pytz.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event isn't over, you can't enter rating.")
    subscription = (await session.scalars(select(Subscription).where(Subscription.user_id == user.id,
                                                                     Subscription.schedule_id == data.schedule_id))).first()
    if data.rating is not None and subscription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't rate as you are not subscribed.")
    if data.rating is None and not data.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't create empty comment.")
    comment = Comment(**data.dict(), schedule=schedule, user=user)
    session.add(comment)
    await session.commit()
    return comment


@router.delete('/{comment_id}', summary='Delete event comment', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID, session: Annotated[Any, Depends(get_async_session)],
                         user: Annotated[User, Depends(get_current_user)]):
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This comment doesn't exist."
        )
    if comment.user != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not owner of this comment."
        )
    await session.delete(comment)


@router.put('/{comment_id}', summary='Update event comment',  response_model=CommentOut)
async def update_comment(comment_id: UUID, data: CommentUpdate, session: Annotated[Any, Depends(get_async_session)],
                         user: Annotated[User, Depends(get_current_user)]):
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This comment doesn't exist."
        )
    if comment.user != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not owner of this comment."
        )
    if data.rating is not None and comment.schedule.scheduled_at > datetime.now(tz=pytz.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event isn't over, you can't enter rating.")
    subscription = (await session.scalars(select(Subscription).where(Subscription.user_id == user.id,
                                                                     Subscription.schedule_id == comment.schedule_id))).first()
    if data.rating is not None and subscription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't rate as you are not subscribed.")
    if data.text:
        comment.text = data.text
    if data.rating:
        comment.rating = data.rating
    await session.commit()
    return comment
