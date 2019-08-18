"""Add user

Revision ID: 403121a8baa3
Revises: 
Create Date: 2019-08-11 15:16:41.846592

"""
from alembic import op
import sqlalchemy as sa

import sys
import os.path
sys.path.append(os.path.abspath("."))

from guid import GUID
from json_field import JSONEncodedDict

# revision identifiers, used by Alembic.
revision = '403121a8baa3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('discord_id', sa.String(length=80), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('discriminator', sa.String(length=4), nullable=False),
        sa.Column('avatar_hash', sa.String(length=120), nullable=True),
        sa.Column('oauth_token', JSONEncodedDict(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
