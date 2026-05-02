"""Adicionar backup_status à GalleryImage

Revision ID: 1e11ffb06e70
Revises: 6d33f41f5d91
Create Date: 2026-04-25 23:26:01.203424

"""
from alembic import op
import sqlalchemy as sa


# identificadores de revisão, usados pelo Alembic.
revision = '1e11ffb06e70'
down_revision = '6d33f41f5d91'
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos gerados automaticamente pelo Alembic - por favor ajuste! ###
    with op.batch_alter_table('gallery_images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('backup_status', sa.Boolean(), nullable=True))

    # ### fim dos comandos do Alembic ###


def downgrade():
    # ### comandos gerados automaticamente pelo Alembic - por favor ajuste! ###
    with op.batch_alter_table('gallery_images', schema=None) as batch_op:
        batch_op.drop_column('backup_status')

    # ### fim dos comandos do Alembic ###
