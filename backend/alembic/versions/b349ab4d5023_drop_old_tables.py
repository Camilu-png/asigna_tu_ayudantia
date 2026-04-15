"""drop old tables

Revision ID: b349ab4d5023
Revises: e59b8088c339
Create Date: 2026-04-15 12:15:02.424896

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b349ab4d5023"
down_revision: Union[str, Sequence[str], None] = "e59b8088c339"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old tables that are no longer needed
    op.drop_table("assistant_courses_new")
    op.drop_table("assistant_schedules")
    op.drop_table("assistants")
    op.drop_table("student_schedules")
    op.drop_table("students")


def downgrade() -> None:
    # Recreate old tables (not implemented)
    pass
