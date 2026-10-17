"""server sitac

Revision ID: 7c2f4a9e1b3d
Revises: 1d905becb4ec
Create Date: 2026-10-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c2f4a9e1b3d'
down_revision: Union[str, None] = '1d905becb4ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('server', sa.Column('dcsbot_name', sa.String(length=255), nullable=True))
    op.add_column('server', sa.Column('sitac_url', sa.String(length=255), nullable=True))
    op.create_unique_constraint('server_dcsbot_name_key', 'server', ['dcsbot_name'])


def downgrade() -> None:
    op.drop_constraint('server_dcsbot_name_key', 'server', type_='unique')
    op.drop_column('server', 'sitac_url')
    op.drop_column('server', 'dcsbot_name')
