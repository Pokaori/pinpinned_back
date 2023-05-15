from typing import Annotated, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from models import User
from serialisers.user import UserOut
from settings.auth import get_current_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", dependencies=[Depends(get_current_user)], response_model=List[UserOut])
async def get_users(session: Annotated[Any, Depends(get_async_session)], ):
    q = await session.execute(select(User).order_by(User.id))
    return q.scalars().all()


@router.get("/{user_id}", dependencies=[Depends(get_current_user)], response_model=UserOut)
async def read_user(user_id: UUID, session: Annotated[Any, Depends(get_async_session)]):
    q = await session.get(User, user_id)
    return q


@router.get('/portfolio', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
