"""empty message

Revision ID: 4e43c66f7d16
Revises: 66ab9d4ffdf0
Create Date: 2023-06-26 20:24:35.314274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e43c66f7d16'
down_revision = '66ab9d4ffdf0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('ever_dormant')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ever_dormant', sa.VARCHAR(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###