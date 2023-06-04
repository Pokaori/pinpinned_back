import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import relationship
from settings import Base
import sqlalchemy as sa


class Subscription(Base):
    __tablename__ = "subscription"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="subscriptions", lazy="selectin")
    schedule_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('event_schedule.id', ondelete="CASCADE"), nullable=False, )
    schedule = relationship("EventSchedule", back_populates="subscriptions", lazy="selectin")
    people_number = sa.Column(sa.Integer,
                              sa.CheckConstraint('people_number > 0 AND people_number < 11', name="people_number_con"),
                              nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    __table_args__ = (UniqueConstraint('schedule_id', 'user_id', name='_foreign_con_user_schedule'),)
