"""Add status_details column to tunnels table

Revision ID: 94bd9d68cee1
Revises:
Create Date: 2025-02-16 13:25:55.395192

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "94bd9d68cee1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tunnels", sa.Column("status_details", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("tunnels", "status_details")
    # ### end Alembic commands ###
