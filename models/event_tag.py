from sqlalchemy import Table, ForeignKey, Column

from settings import Base

event_tag_table = Table(
    "event_tag",
    Base.metadata,
    Column("tag_name", ForeignKey("tag.name", ondelete="CASCADE"), primary_key=True, nullable=False),
    Column("event_id", ForeignKey("event.id", ondelete="CASCADE"), primary_key=True, nullable=False),
)