from datetime import timedelta, datetime
from typing import Annotated, Any

import jwt
from fastapi import HTTPException, Header
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.future import select
from starlette import status

from models import User
from serialisers.user import UserOut, TokenPayload
from settings import config
from settings.config import JWT_SECRET_KEY, ALGORITHM, JWT_REFRESH_SECRET_KEY
from settings.db import get_async_session

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)


async def get_current_user(token: Annotated[Any, Depends(reuseable_oauth)], session: Annotated[Any, Depends(get_async_session)]) -> UserOut:
    return await _get_token_user(token, JWT_SECRET_KEY, session)


async def get_refresh_user(authorization: Annotated[str, Header()], session: Annotated[Any, Depends(get_async_session)]) -> UserOut:
    return await _get_token_user(authorization.split("Bearer ")[1], JWT_REFRESH_SECRET_KEY, session)


async def _get_token_user(token: str, key: str, session: Annotated[Any, Depends(get_async_session)]) -> UserOut:
    try:
        payload = jwt.decode(
            token, key, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.exceptions.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (await session.scalars(select(User).where(User.email == token_data.sub))).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user


def __create_token(subject: str, minutes: int, key: str, expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + timedelta(expires_delta)
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, key, config.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str, expires_delta: int = None) -> str:
    return __create_token(subject, config.ACCESS_TOKEN_EXPIRE_MINUTES, config.JWT_SECRET_KEY, expires_delta)


def create_refresh_token(subject: str, expires_delta: int = None) -> str:
    return __create_token(subject, config.REFRESH_TOKEN_EXPIRE_MINUTES, config.JWT_REFRESH_SECRET_KEY, expires_delta)
