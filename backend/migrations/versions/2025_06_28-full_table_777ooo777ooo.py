"""Full table

Revision ID: 3c9e02eca479
Revises: 
Create Date: 2025-06-13 15:00:05.356759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c9e02eca479'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('region',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('ref_count', sa.Integer(), nullable=False),
    sa.Column('refer_from_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['refer_from_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('server',
    sa.Column('ip_address', sa.String(length=16), nullable=False),
    sa.Column('domain_name', sa.String(length=64), nullable=False),
    sa.Column('protocol', sa.Enum('openvpn', 'vless', name='vpnprotocol'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('max_certificates', sa.Integer(), nullable=False),
    sa.Column('current_cert_count', sa.Integer(), nullable=False),
    sa.Column('region_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ip_address'),
    sa.UniqueConstraint('domain_name') 
    )
    op.create_table('subscription',
    sa.Column('type', sa.Enum('trial', 'devices_2', 'devices_4', name='subscriptiontype'), nullable=False),
    sa.Column('protocol', sa.Enum('openvpn', 'vless', name='vpnprotocol'), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('region_id', sa.BigInteger(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subscriptionprice',
    sa.Column('type', sa.Enum('trial', 'devices_2', 'devices_4', name='subscriptiontype'), nullable=False),
    sa.Column('duration', sa.Enum('month_1', 'month_6', 'year_1', name='subscriptionduration'), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('region_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type', 'duration', 'region_id', name='uniq_price_tariff')
    )
    op.create_table('certificate',
    sa.Column('filename', sa.String(length=1024), nullable=False),
    sa.Column('url_vless', sa.Text(), nullable=True),
    sa.Column('server_id', sa.BigInteger(), nullable=True),
    sa.Column('subscription_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('filename'),
    sa.UniqueConstraint('url_vless')
    )
    op.create_table('payment',
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('provider', sa.String(length=64), nullable=False),
    sa.Column('status', sa.Enum('success', 'pending', 'failed', name='paymentstatus'), nullable=False),
    sa.Column('operation_id', sa.String(length=128), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('intent_data', sa.JSON(), nullable=True),
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
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('certificate')
    op.drop_table('subscriptionprice')
    op.drop_table('subscription')
    op.drop_table('server')
    op.drop_table('user')
    op.drop_table('region')
    # Удаление Enum типов данных из БД
    op.execute('DROP TYPE IF EXISTS subscriptiontype')
    op.execute('DROP TYPE IF EXISTS subscriptionduration')
    op.execute('DROP TYPE IF EXISTS vpnprotocol')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    # ### end Alembic commands ###
