"""empty message

Revision ID: 4ba6c1670855
Revises: 2c8d3ec3d035
Create Date: 2023-06-22 16:20:05.614363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ba6c1670855'
down_revision = '2c8d3ec3d035'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('account_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('saldo', sa.Integer(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['branch_id'], ['branch.branch_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('account_activity',
    sa.Column('activity_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('activity_date', sa.DateTime(), nullable=False),
    sa.Column('credit', sa.Integer(), nullable=True),
    sa.Column('debit', sa.Integer(), nullable=True),
    sa.Column('receiver_id', sa.Integer(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('saldo', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.account_id'], ),
    sa.ForeignKeyConstraint(['receiver_id'], ['account.account_id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['account.account_id'], ),
    sa.PrimaryKeyConstraint('activity_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account_activity')
    op.drop_table('account')
    # ### end Alembic commands ###
