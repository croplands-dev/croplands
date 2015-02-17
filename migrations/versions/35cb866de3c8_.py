"""empty message

Revision ID: 35cb866de3c8
Revises: 46fcf571dd27
Create Date: 2015-02-11 09:17:28.037954

"""

# revision identifiers, used by Alembic.
revision = '35cb866de3c8'
down_revision = '46fcf571dd27'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('record', sa.Column('rating', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('record', 'rating')
    ### end Alembic commands ###