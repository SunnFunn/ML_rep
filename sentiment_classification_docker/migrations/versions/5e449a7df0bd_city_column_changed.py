"""city column changed

Revision ID: 5e449a7df0bd
Revises: 3f86b5b23610
Create Date: 2022-06-01 16:35:17.835130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e449a7df0bd'
down_revision = '3f86b5b23610'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_city', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_city', 'user', ['city'], unique=False)
    # ### end Alembic commands ###
