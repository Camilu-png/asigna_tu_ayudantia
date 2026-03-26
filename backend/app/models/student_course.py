from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from app.db.base import Base
from app.models.constants import DEFAULT_COURSE_COLOR


class StudentCourse(Base):
    __tablename__ = "student_courses"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    time_block_id: Mapped[int] = mapped_column(
        ForeignKey("time_blocks.id"), primary_key=True
    )
    color: Mapped[str] = mapped_column(String(7), default=DEFAULT_COURSE_COLOR)

    student: Mapped["Student"] = relationship(back_populates="student_courses")
    course: Mapped["Course"] = relationship(back_populates="student_courses")
    time_block: Mapped["TimeBlock"] = relationship(back_populates="student_courses")


class AssistantCourse(Base):
    __tablename__ = "assistant_courses"

    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistants.id"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    time_block_id: Mapped[int] = mapped_column(
        ForeignKey("time_blocks.id"), primary_key=True
    )
    color: Mapped[str] = mapped_column(String(7), default=DEFAULT_COURSE_COLOR)

    assistant: Mapped["Assistant"] = relationship(back_populates="assistant_courses")
    course: Mapped["Course"] = relationship(back_populates="assistant_courses")
    time_block: Mapped["TimeBlock"] = relationship(back_populates="assistant_courses")
