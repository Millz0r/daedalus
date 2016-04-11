"""create caller table

Revision ID: 1f1fe4b205ef
Revises: 
Create Date: 2015-03-17 01:27:37.290674

"""

# revision identifiers, used by Alembic.
revision = '1f1fe4b205ef'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import table, column


def upgrade():
    op.create_table(
        'callers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(32), nullable=False),
        sa.Column('token', sa.String(128)),
        sa.Column('description', sa.String()),
    )
    # insert default data
    callers_table = table(
        'callers',
        column('username', sa.String),
        column('token', sa.String),
        column('description', sa.String),
    )
    op.bulk_insert(
        callers_table,
        [
            {'username': 'yambo', 'token': 'groot?'},
        ]
    )

def downgrade():
    op.drop_table('callers')
