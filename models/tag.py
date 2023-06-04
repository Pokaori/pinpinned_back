from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, column_property

from .event_tag import event_tag_table
from settings import Base
import sqlalchemy as sa


class Tag(Base):
    __tablename__ = "tag"
    name = sa.Column(sa.String, sa.CheckConstraint(r"regexp_like([\w_-]+)", name="tag_name"), primary_key=True)
    events = relationship("Event", secondary=event_tag_table, back_populates="tags", lazy='joined')
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    event_count = column_property(
        select(func.count(event_tag_table.c.event_id)).where(event_tag_table.c.tag_name == name).scalar_subquery()
    )
