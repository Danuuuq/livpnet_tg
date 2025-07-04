"""Add table with payment and referal

Revision ID: 8adde31b0f9a
Revises: 3c9e02eca479
Create Date: 2025-06-21 19:54:10.625630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8adde31b0f9a'
down_revision: Union[str, None] = '3c9e02eca479'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('provider', sa.String(length=64), nullable=False),
    sa.Column('status', sa.Enum('success', 'pending', 'failed', name='paymentstatus'), nullable=False),
    sa.Column('operation_id', sa.String(length=128), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('operation_id')
    )
    op.create_table('referralbonus',
    sa.Column('bonus_given', sa.Boolean(), nullable=False),
    sa.Column('bonus_size', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('invited_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['invited_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'invited_id', name='uq_user_invited')
    )
    op.alter_column('server', 'region_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.create_unique_constraint(None, 'server', ['domain_name'])
    op.alter_column('subscription', 'user_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('subscription', 'user_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.drop_constraint(None, 'server', type_='unique')
    op.alter_column('server', 'region_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.drop_table('referralbonus')
    op.drop_table('payment')
    # Удаление Enum типов данных из БД
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    # ### end Alembic commands ###
