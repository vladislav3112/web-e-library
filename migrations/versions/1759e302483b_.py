"""empty message

Revision ID: 1759e302483b
Revises: a41e188f8517
Create Date: 2020-11-13 18:16:13.289127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1759e302483b'
down_revision = 'a41e188f8517'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('book', sa.Column('image', sa.LargeBinary(), nullable=True))
    op.create_unique_constraint(None, 'book', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'book', type_='unique')
    op.drop_column('book', 'image')
    # ### end Alembic commands ###
