"""status

Revision ID: 4a0f89c5dccb
Revises: 51081db5e269
Create Date: 2024-12-08 14:10:45.924768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a0f89c5dccb'
down_revision: Union[str, None] = '51081db5e269'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Шаг 1: Добавить столбец с допустимыми NULL значениями
    op.add_column('users', sa.Column('online_status', sa.Boolean(), nullable=True))

    # Шаг 2: Установить значение по умолчанию для существующих строк
    op.execute('UPDATE users SET online_status = false WHERE online_status IS NULL')

    # Шаг 3: Изменить столбец, чтобы он не допускал NULL значений
    op.alter_column('users', 'online_status', nullable=False)


def downgrade():
    # Шаг 1: Изменить столбец, чтобы он допускал NULL значения
    op.alter_column('users', 'online_status', nullable=True)

    # Шаг 2: Удалить столбец
    op.drop_column('users', 'online_status')
