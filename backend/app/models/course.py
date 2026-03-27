from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.db.base import Base
from app.models.student_course import StudentCourse, AssistantCourse


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    professor: Mapped[str] = mapped_column(String(255), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)

    time_blocks: Mapped[list["TimeBlock"]] = relationship(back_populates="course")
    student_courses: Mapped[list["StudentCourse"]] = relationship(
        back_populates="course"
    )
    assistant_courses: Mapped[list["AssistantCourse"]] = relationship(
        back_populates="course"
    )
