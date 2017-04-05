"""body to LONGTEXT

Revision ID: f2dc9e2fc4fe
Revises: 3aa806a7230d
Create Date: 2017-03-22 06:17:56.211129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2dc9e2fc4fe'
down_revision = '3aa806a7230d'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.sql.text('ALTER TABLE email MODIFY body LONGTEXT;'))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.sql.text('ALTER TABLE email MODIFY body MEDIUMTEXT;'))
