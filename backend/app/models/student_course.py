from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from app.db.base import Base


class StudentCourse(Base):
    __tablename__ = "student_courses"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    time_block_id: Mapped[int] = mapped_column(
        ForeignKey("time_blocks.id"), primary_key=True
    )
    color: Mapped[str] = mapped_column(String(7), default="#4ECDC4")


class AssistantCourse(Base):
    __tablename__ = "assistant_courses"

    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistants.id"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    time_block_id: Mapped[int] = mapped_column(
        ForeignKey("time_blocks.id"), primary_key=True
    )
    color: Mapped[str] = mapped_column(String(7), default="#4ECDC4")
