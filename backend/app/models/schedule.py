from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base
from app.models.assistant_help_block import AssistantHelpBlock


class ScheduleBlock(Base):
    __tablename__ = "schedule_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=True)

    course: Mapped["Course"] = relationship(back_populates="schedule_blocks")
    assistant_help_blocks: Mapped[list["AssistantHelpBlock"]] = relationship(
        back_populates="schedule_block"
    )
    user_schedules: Mapped[list["UserSchedule"]] = relationship(
        back_populates="schedule_block"
    )


class UserSchedule(Base):
    __tablename__ = "user_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    schedule_block_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_blocks.id"), nullable=False
    )
    color: Mapped[str] = mapped_column(String(7), nullable=True)

    user: Mapped["User"] = relationship(back_populates="user_schedules")
    schedule_block: Mapped["ScheduleBlock"] = relationship(
        back_populates="user_schedules"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "schedule_block_id", name="uq_user_schedule"),
    )
