"""Adicionar definições de API ao modelo User

Revision ID: 8dc30e76d3a0
Revises: 1e11ffb06e70
Create Date: 2026-05-02 01:41:27.474438

"""
from alembic import op
import sqlalchemy as sa


# identificadores de revisão, usados pelo Alembic.
revision = '8dc30e76d3a0'
down_revision = '1e11ffb06e70'
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos gerados automaticamente pelo Alembic - por favor ajuste! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_astrometry_api_key', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('telescopius_base_url', sa.String(length=256), nullable=True))

    # ### fim dos comandos do Alembic ###


def downgrade():
    # ### comandos gerados automaticamente pelo Alembic - por favor ajuste! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('telescopius_base_url')
        batch_op.drop_column('_astrometry_api_key')

    # ### fim dos comandos do Alembic ###
