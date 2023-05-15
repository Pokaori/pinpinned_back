from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy_utils import PhoneNumberParseException
from starlette import status

from models import User
from serialisers.user import UserAuth, UserOut, TokenSchema, TokenSchemaAccess
from settings.auth import create_access_token, create_refresh_token, get_refresh_user
from settings.db import get_async_session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth, session: Annotated[Any, Depends(get_async_session)]):
    user = await session.scalars(select(User).where(User.email == data.email))
    if user.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    try:
        user = data.dict()
        session.add(User(**user))
        await session.commit()
        return (await session.scalars(select(User).where(User.email == data.email))).first()
    except PhoneNumberParseException as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Any, Depends(get_async_session)]):
    user = (await session.scalars(select(User).where(User.email == data.username))).first()
    if user is None or user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@router.get('/refresh', summary='Refresh token', response_model=TokenSchemaAccess)
async def refresh_token(user: User = Depends(get_refresh_user)):
    return {
        "access_token": create_access_token(user.email)
    }
