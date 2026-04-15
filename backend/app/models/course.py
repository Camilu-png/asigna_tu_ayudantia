from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.db.base import Base
from app.models.schedule import ScheduleBlock
from app.models.assistant_course import AssistantCourse
from app.models.assistant_help_block import AssistantHelpBlock
from app.models.user_course import UserCourse


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    professor: Mapped[str] = mapped_column(String(255), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)

    schedule_blocks: Mapped[list["ScheduleBlock"]] = relationship(
        back_populates="course"
    )
    assistant_courses_new: Mapped[list["AssistantCourse"]] = relationship(
        back_populates="course"
    )
    assistant_help_blocks: Mapped[list["AssistantHelpBlock"]] = relationship(
        back_populates="course"
    )
    user_courses: Mapped[list["UserCourse"]] = relationship(back_populates="course")
