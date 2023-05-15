import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from settings import Base
import sqlalchemy as sa


class EventSchedule(Base):
    __tablename__ = "event_schedule"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('event.id', ondelete="CASCADE"), nullable=False)
    event = relationship("Event", back_populates="schedules", lazy='selectin')
    scheduled_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

