import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import relationship
from settings import Base
import sqlalchemy as sa


class Comment(Base):
    __tablename__ = "comment"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="comments", lazy='joined')
    schedule_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('event_schedule.id', ondelete="CASCADE"), nullable=False)
    schedule = relationship("EventSchedule", back_populates="comments", lazy='selectin')
    text = sa.Column(sa.String())
    rating = sa.Column(sa.Integer(), sa.CheckConstraint('rating >=0 AND rating < 6', name="rating_con"))
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

