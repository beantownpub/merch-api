"""Testing

Revision ID: c9aec6b302df
Revises: ad83eb25c7ee
Create Date: 2022-04-02 14:55:21.276709

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9aec6b302df'
down_revision = 'ad83eb25c7ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'foos', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'foos', type_='unique')
    # ### end Alembic commands ###