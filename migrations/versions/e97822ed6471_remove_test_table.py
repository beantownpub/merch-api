"""Remove test table

Revision ID: e97822ed6471
Revises: c9aec6b302df
Create Date: 2022-04-02 15:00:33.882467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e97822ed6471'
down_revision = 'c9aec6b302df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('foos')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('foos',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='foos_pkey'),
    sa.UniqueConstraint('id', name='foos_id_key')
    )
    # ### end Alembic commands ###
