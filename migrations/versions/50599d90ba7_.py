"""empty message

Revision ID: 50599d90ba7
Revises: 55351f83bf33
Create Date: 2015-04-16 16:45:44.527232

"""

# revision identifiers, used by Alembic.
revision = '50599d90ba7'
down_revision = '55351f83bf33'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('location', sa.Column('use_verification_locked', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('location', 'use_verification_locked')
    ### end Alembic commands ###
