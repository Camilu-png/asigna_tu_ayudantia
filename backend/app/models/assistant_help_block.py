from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base
from app.models.constants import DEFAULT_COURSE_COLOR


class AssistantHelpBlock(Base):
    __tablename__ = "assistant_help_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistants.id"), nullable=False
    )
    schedule_block_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_blocks.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=True)

    assistant: Mapped["Assistant"] = relationship(back_populates="help_blocks")
    schedule_block: Mapped["ScheduleBlock"] = relationship(
        back_populates="assistant_help_blocks"
    )
    course: Mapped["Course"] = relationship(back_populates="assistant_help_blocks")

    __table_args__ = (
        UniqueConstraint(
            "assistant_id", "schedule_block_id", name="uq_assistant_help_block"
        ),
    )
