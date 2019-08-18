"""Connections

Revision ID: d6fc023e9fd8
Revises: 403121a8baa3
Create Date: 2019-08-11 22:16:01.192317

"""
from alembic import op
import sqlalchemy as sa

import sys
import os.path
sys.path.append(os.path.abspath("."))

from guid import GUID

# revision identifiers, used by Alembic.
revision = 'd6fc023e9fd8'
down_revision = '403121a8baa3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('connection',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('discord_id', sa.String(length=80), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('kind', sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('connection')
    # ### end Alembic commands ###