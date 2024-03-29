"""create event

Revision ID: 56b46dbbe5dc
Revises: c3ada914373a
Create Date: 2023-05-11 23:07:33.009808

"""
import geoalchemy2
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '56b46dbbe5dc'
down_revision = 'c3ada914373a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration', sa.Integer(),sa.CheckConstraint('duration > 0 AND duration < 25', name="duration_con"), nullable=False ),
    sa.Column('fee', sa.Float(), nullable=True),
    sa.Column('place', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('index_event_place', 'event', ['place'], unique=False, postgresql_using='gist')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('index_event_place', table_name='event', postgresql_using='gist')
    op.drop_table('event')
    # ### end Alembic commands ###
