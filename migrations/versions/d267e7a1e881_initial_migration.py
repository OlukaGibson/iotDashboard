"""Initial migration.

Revision ID: d267e7a1e881
Revises: 220ff39116a3
Create Date: 2024-07-10 14:06:02.205572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd267e7a1e881'
down_revision = '220ff39116a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('firmware',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firmwareVersion', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('firmwareVersion')
    )
    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deviceID', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('firmwareVersion', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(None, ['writekey'])
        batch_op.create_unique_constraint(None, ['deviceID'])
        batch_op.create_unique_constraint(None, ['name'])
        batch_op.create_unique_constraint(None, ['readkey'])
        batch_op.create_foreign_key(None, 'firmware', ['firmwareVersion'], ['id'])

    with op.batch_alter_table('metadatavalues', schema=None) as batch_op:
        batch_op.drop_constraint('metadatavalues_deviceID_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'devices', ['deviceID'], ['deviceID'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('metadatavalues', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('metadatavalues_deviceID_fkey', 'devices', ['deviceID'], ['id'])

    with op.batch_alter_table('devices', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('firmwareVersion')
        batch_op.drop_column('deviceID')

    op.drop_table('firmware')
    # ### end Alembic commands ###
