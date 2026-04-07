from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base
from app.models.constants import DEFAULT_COURSE_COLOR
from app.models.assistant_help_block import AssistantHelpBlock


class ScheduleBlock(Base):
    __tablename__ = "schedule_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=True)

    course: Mapped["Course"] = relationship(back_populates="schedule_blocks")
    student_schedules: Mapped[list["StudentSchedule"]] = relationship(
        back_populates="schedule_block"
    )
    assistant_schedules: Mapped[list["AssistantSchedule"]] = relationship(
        back_populates="schedule_block"
    )
    assistant_help_blocks: Mapped[list["AssistantHelpBlock"]] = relationship(
        back_populates="schedule_block"
    )


class StudentSchedule(Base):
    __tablename__ = "student_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    schedule_block_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_blocks.id"), nullable=False
    )
    color: Mapped[str] = mapped_column(String(7), default=DEFAULT_COURSE_COLOR)

    student: Mapped["Student"] = relationship(back_populates="student_schedules")
    schedule_block: Mapped["ScheduleBlock"] = relationship(
        back_populates="student_schedules"
    )

    __table_args__ = (
        UniqueConstraint("student_id", "schedule_block_id", name="uq_student_schedule"),
    )


class AssistantSchedule(Base):
    __tablename__ = "assistant_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistants.id"), nullable=False
    )
    schedule_block_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_blocks.id"), nullable=False
    )
    color: Mapped[str] = mapped_column(String(7), default=DEFAULT_COURSE_COLOR)

    assistant: Mapped["Assistant"] = relationship(back_populates="assistant_schedules")
    schedule_block: Mapped["ScheduleBlock"] = relationship(
        back_populates="assistant_schedules"
    )

    __table_args__ = (
        UniqueConstraint(
            "assistant_id", "schedule_block_id", name="uq_assistant_schedule"
        ),
    )
