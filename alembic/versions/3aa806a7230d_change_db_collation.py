"""change db collation

Revision ID: 3aa806a7230d
Revises: 0284b2835cc7
Create Date: 2017-03-22 06:05:32.908543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3aa806a7230d'
down_revision = '0284b2835cc7'
branch_labels = None
depends_on = None




def upgrade():
    conn = op.get_bind()
    conn.execute(sa.sql.text('ALTER table email CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.sql.text('ALTER table email CONVERT TO CHARACTER SET latin1 COLLATE latin1_swedish_ci'))
