"""unify users and roles - manual migration

Revision ID: e59b8088c339
Revises:
Create Date: 2026-04-15 11:51:59.330077

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e59b8088c339"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ASSISTANT_ID_OFFSET = 100

    # Clear any pre-existing data in new tables
    op.execute("DELETE FROM user_schedules")
    op.execute("DELETE FROM user_courses")
    op.execute("DELETE FROM users")

    # ============================================
    # 1. DROP TABLES WITH DEPENDENCIES FIRST
    # ============================================

    # Drop tables with FK to students/assistants BEFORE dropping them
    op.drop_table("student_courses")
    op.drop_table("assistant_courses")
    op.drop_table("solutions")
    op.drop_table("time_blocks")

    # Drop FK from assistant_help_blocks to assistants
    op.drop_constraint(
        "assistant_help_blocks_assistant_id_fkey",
        "assistant_help_blocks",
        type_="foreignkey",
    )

    # ============================================
    # 2. MIGRATE DATA FROM STUDENTS & ASSISTANTS
    # ============================================

    # Migrate students to users (keep original IDs: 1, 2)
    op.execute("""
        INSERT INTO users (id, name, email, password)
        SELECT id, name, email, password FROM students
    """)

    # Migrate assistants to users (with offset: 100+id)
    op.execute(f"""
        INSERT INTO users (id, name, email, password)
        SELECT ({ASSISTANT_ID_OFFSET} + id), name, email, password FROM assistants
    """)

    # ============================================
    # 3. MIGRATE DATA TO USER_COURSES
    # ============================================

    # Migrate assistant_courses_new -> user_courses (role = ASSISTANT)
    op.execute(f"""
        INSERT INTO user_courses (user_id, course_id, role, color)
        SELECT ({ASSISTANT_ID_OFFSET} + assistant_id), course_id, 'ASSISTANT', color 
        FROM assistant_courses_new
    """)

    # ============================================
    # 4. MIGRATE DATA TO USER_SCHEDULES
    # ============================================

    # Migrate student_schedules -> user_schedules
    op.execute("""
        INSERT INTO user_schedules (user_id, schedule_block_id, color)
        SELECT student_id, schedule_block_id, color FROM student_schedules
    """)

    # Migrate assistant_schedules -> user_schedules (with offset)
    op.execute(f"""
        INSERT INTO user_schedules (user_id, schedule_block_id, color)
        SELECT ({ASSISTANT_ID_OFFSET} + assistant_id), schedule_block_id, color 
        FROM assistant_schedules
    """)

    # ============================================
    # 5. UPDATE ASSISTANT_HELP_BLOCKS REFERENCES
    # ============================================

    # Update assistant_id in assistant_help_blocks to use new offset
    op.execute(f"""
        UPDATE assistant_help_blocks 
        SET assistant_id = ({ASSISTANT_ID_OFFSET} + assistant_id)
    """)

    # Add new FK referencing users table
    op.create_foreign_key(
        "assistant_help_blocks_user_id_fkey",
        "assistant_help_blocks",
        "users",
        ["assistant_id"],
        ["id"],
    )

    # ============================================
    # 6. DROP OLD TABLES
    # ============================================

    op.drop_table("student_schedules")
    op.drop_table("assistant_schedules")
    op.drop_table("assistant_courses_new")
    op.drop_table("students")
    op.drop_table("assistants")


def downgrade() -> None:
    # Downgrade not implemented for this complex migration
    pass
