"""Added qr_code and entry_status columns

Revision ID: 830ac4983f65
Revises: 
Create Date: 2025-03-11 21:44:54.348426

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '830ac4983f65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('qr_code', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('entry_status', sa.Enum('Not Scanned', 'Scanned'), nullable=True))
        batch_op.alter_column('plan_type',
               existing_type=mysql.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.create_unique_constraint(None, ['qr_code'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('plan_type',
               existing_type=sa.String(length=50),
               type_=mysql.TEXT(),
               existing_nullable=False)
        batch_op.drop_column('entry_status')
        batch_op.drop_column('qr_code')

    # ### end Alembic commands ###
