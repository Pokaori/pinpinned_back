from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.future import select
from starlette import status

from models import EventSchedule
from models.subscription import Subscription
from settings.auth import get_current_user
from models.user import User
from serialisers.subscription import SubscriptionOut, SubscriptionCreate
from settings.db import get_async_session

router = APIRouter(
    prefix="/subscription",
    tags=["subscription"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', summary='Create event subscription', response_model=SubscriptionOut)
async def create_subscription(data: SubscriptionCreate,
                              session: Annotated[Any, Depends(get_async_session)],
                              user: Annotated[User, Depends(get_current_user)]):
    schedule = await session.get(EventSchedule, data.schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event does not exist")
    if schedule.scheduled_at > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Event is over, you can't delete subscription")
    if schedule.event.author == user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user is owner of this event.")
    subscription = (await session.scalars(
        select(Subscription).where(Subscription.schedule_id == data.schedule_id).where(
            Subscription.user_id == user.id))).first()
    if subscription is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already subscribed.")
    if schedule.event.place_number < (schedule.places_sub or 0 + data.people_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There are no empty spaces.")
    subscription = Subscription(**data.dict(), schedule=schedule, user=user)
    session.add(subscription)
    await session.commit()
    return subscription


@router.delete('/{subscription_id}', summary='Delete event subscription', status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(subscription_id: UUID, session: Annotated[Any, Depends(get_async_session)],
                              user: Annotated[User, Depends(get_current_user)]):
    subscription = await session.get(Subscription, subscription_id)
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not subscribed."
        )
    if subscription.user != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not owner of this subscription."
        )
    schedule = await session.get(EventSchedule, subscription.schedule_id)
    if schedule.scheduled_at > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is over, you can't unsubscription")
    await session.delete(subscription)


@router.get('/', summary='Get all user subscription', response_model=list[SubscriptionOut])
async def get_subscriptions(session: Annotated[Any, Depends(get_async_session)],
                            user: Annotated[User, Depends(get_current_user)]):
    subscriptions = (await session.scalars(select(Subscription).where(Subscription.user_id == user.id))).unique().all()
    return subscriptions
