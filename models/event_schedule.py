import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, column_property

from .subscription import Subscription
from settings import Base
import sqlalchemy as sa


class EventSchedule(Base):
    __tablename__ = "event_schedule"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('event.id', ondelete="CASCADE"), nullable=False)
    event = relationship("Event", back_populates="schedules", lazy='joined')
    scheduled_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    subscriptions = relationship("Subscription", back_populates="schedule", lazy="joined")
    comments = relationship("Comment", back_populates="schedule", lazy="joined")
    is_canceled = sa.Column(sa.Boolean, nullable=False, default=False)
    places_sub = column_property(
        select(func.coalesce(func.sum(Subscription.people_number),0)).where(Subscription.schedule_id == id).scalar_subquery()
    )
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
