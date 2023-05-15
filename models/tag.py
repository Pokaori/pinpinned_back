from sqlalchemy import func
from sqlalchemy.orm import relationship

from .event_tag import event_tag_table
from settings import Base
import sqlalchemy as sa

from settings.db import get_async_session


class Tag(Base):
    __tablename__ = "tag"
    name = sa.Column(sa.String, sa.CheckConstraint(r"regexp_like([\w_-]+)", name="tag_name"), primary_key=True)
    events = relationship("Event", secondary=event_tag_table, back_populates="tags", lazy='selectin')
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    @property
    async def event_number(self):
        session = await get_async_session()
        res = (await session.execute(func.count(self.events))).scalars().first()
        print(res)
        return res

