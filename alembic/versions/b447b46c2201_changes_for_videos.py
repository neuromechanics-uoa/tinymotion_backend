"""changes for videos

Revision ID: b447b46c2201
Revises: 2c3b3a04809b
Create Date: 2024-02-23 14:42:00.189494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b447b46c2201'
down_revision: Union[str, None] = '2c3b3a04809b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('video_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
        batch_op.create_index(batch_op.f('ix_video_video_name'), ['video_name'], unique=True)
        batch_op.drop_column('file_name')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_name', sa.VARCHAR(), nullable=False))
        batch_op.drop_index(batch_op.f('ix_video_video_name'))
        batch_op.drop_column('video_name')

    # ### end Alembic commands ###