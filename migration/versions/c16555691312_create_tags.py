"""create tags

Revision ID: c16555691312
Revises: 7c657a14600a
Create Date: 2023-05-15 20:10:44.031485

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c16555691312'
down_revision = '7c657a14600a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('event_tag',
    sa.Column('tag_name', sa.String(), nullable=False),
    sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_name'], ['tag.name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tag_name', 'event_id')
    )
    op.drop_constraint('event_author_id_fkey', 'event', type_='foreignkey')
    op.create_foreign_key(None, 'event', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('event_schedule_event_id_fkey', 'event_schedule', type_='foreignkey')
    op.create_foreign_key(None, 'event_schedule', 'event', ['event_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'event_schedule', type_='foreignkey')
    op.create_foreign_key('event_schedule_event_id_fkey', 'event_schedule', 'event', ['event_id'], ['id'])
    op.drop_constraint(None, 'event', type_='foreignkey')
    op.create_foreign_key('event_author_id_fkey', 'event', 'user', ['author_id'], ['id'])
    op.drop_table('event_tag')
    op.drop_table('tag')
    # ### end Alembic commands ###
