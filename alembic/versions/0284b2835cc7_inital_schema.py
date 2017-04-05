"""Inital schema

Revision ID: 0284b2835cc7
Revises:
Create Date: 2017-03-18 02:44:07.997834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0284b2835cc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('email',
                    sa.Column('uuid', sa.String(37),
                              primary_key=True, unique=True),
                    sa.Column('from_addr', sa.String(256), nullable=False),
                    sa.Column('to_addr', sa.String(256), nullable=False),
                    sa.Column('subject', sa.String(78), nullable=False),
                    sa.Column('body', sa.Text, nullable=False),
                    sa.Column('created_at', sa.DateTime, nullable=False),
                    sa.Column('deleted_at', sa.DateTime),
                    sa.Column('last_attempt', sa.DateTime),
                    sa.Column('attempts', sa.Integer),
                    sa.Column('status', sa.String(10)),
                    sa.Column('status_code', sa.Integer))


def downgrade():
    op.drop_table('email')
