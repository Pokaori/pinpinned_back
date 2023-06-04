import enum
import uuid

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType, PasswordType, PhoneNumberType

from settings.db import Base


class GenderChoices(enum.StrEnum):
    MAN = enum.auto()
    WOMAN = enum.auto()
    UNDEFINED = enum.auto()


class User(Base):
    __tablename__ = "user"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    email = sa.Column(EmailType, unique=True, index=True)
    password = sa.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    phone_number = sa.Column(PhoneNumberType(region="UA"))
    date_of_birth = sa.Column(sa.Date)
    gender = sa.Column(sa.Enum(GenderChoices), default=GenderChoices.UNDEFINED)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    email_verified = sa.Column(sa.Boolean, default=False)
    events = relationship("Event", back_populates="author")
    subscriptions = relationship("Subscription", back_populates="user", lazy='joined')
    comments = relationship("Comment", back_populates="user", lazy='joined')
