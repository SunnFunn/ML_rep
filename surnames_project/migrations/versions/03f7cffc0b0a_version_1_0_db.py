"""version 1.0 db

Revision ID: 03f7cffc0b0a
Revises: 
Create Date: 2022-06-09 17:18:58.703652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03f7cffc0b0a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('profession', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('surnames',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('surname_beginning', sa.String(length=140), nullable=True),
    sa.Column('surnames_generated', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_surnames_timestamp'), 'surnames', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_surnames_timestamp'), table_name='surnames')
    op.drop_table('surnames')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
