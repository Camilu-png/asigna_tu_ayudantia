from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from app.db.base import Base


class UserCourse(Base):
    __tablename__ = "user_courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=True)

    user: Mapped["User"] = relationship(back_populates="user_courses")
    course: Mapped["Course"] = relationship(back_populates="user_courses")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "role", name="uq_user_course_role"),
        CheckConstraint("role IN ('STUDENT', 'ASSISTANT')", name="ck_role_valid"),
    )
