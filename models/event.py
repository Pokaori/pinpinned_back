import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, column_property
from geoalchemy2.types import Geography

from .subscription import Subscription
from .event_tag import event_tag_table
from settings import Base
import sqlalchemy as sa


class Event(Base):
    __tablename__ = "event"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = sa.Column(sa.String(length=100), nullable=False)
    author_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    author = relationship("User", back_populates="events", lazy='selectin')
    description = sa.Column(TEXT)
    duration = sa.Column(sa.Integer, sa.CheckConstraint('duration > 0 AND duration < 25', name="duration_con"),
                         nullable=False)
    fee = sa.Column(sa.Float, nullable=False, server_default="0")
    place = sa.Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    schedules = relationship("EventSchedule", back_populates="event", lazy='selectin')
    tags = relationship("Tag", secondary=event_tag_table, back_populates="events", lazy='joined')
    place_number = sa.Column(sa.Integer, sa.CheckConstraint('duration > 0 AND duration < 25', name="duration_con"),
                             nullable=False)

