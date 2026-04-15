"""add role and admin user

Revision ID: ce0e423ebfed
Revises: b349ab4d5023
Create Date: 2026-04-15 13:00:15.772721

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ce0e423ebfed"
down_revision: Union[str, Sequence[str], None] = "b349ab4d5023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add role column with default 'USER'
    op.add_column(
        "users", sa.Column("role", sa.String(20), nullable=False, server_default="USER")
    )

    # 2. Add check constraint for role values
    op.create_check_constraint(
        "ck_user_role_valid", "users", "role IN ('USER', 'ADMIN')"
    )

    # 3. Create admin user (using ID 1000 to avoid collision)
    op.execute("""
        INSERT INTO users (id, name, email, password, role)
        VALUES (
            1000,
            'Abatista',
            'abatista@admin.cl',
            '$2b$12$GJKgtnkemf.15hs5a4R99.KCnKwmoKSJsGQbOihWDDWHu3v0jHbTS',
            'ADMIN'
        )
    """)


def downgrade() -> None:
    # Remove admin user
    op.execute("DELETE FROM users WHERE email = 'abatista@admin.cl'")

    # Drop check constraint
    op.drop_constraint("ck_user_role_valid", "users", type_="check")

    # Drop role column
    op.drop_column("users", "role")
