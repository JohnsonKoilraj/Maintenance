"""service

Revision ID: 1dfcd88303e3
Revises: 062d0d146ffd
Create Date: 2023-11-15 17:38:00.124235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dfcd88303e3'
down_revision: Union[str, None] = '062d0d146ffd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('f_name', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('l_name', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('city', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('state', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('country', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'country')
    op.drop_column('user', 'state')
    op.drop_column('user', 'city')
    op.drop_column('user', 'l_name')
    op.drop_column('user', 'f_name')
    # ### end Alembic commands ###
