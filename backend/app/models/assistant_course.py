from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from app.db.base import Base
from app.models.constants import DEFAULT_COURSE_COLOR


class AssistantCourse(Base):
    __tablename__ = "assistant_courses_new"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("assistants.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default=DEFAULT_COURSE_COLOR)

    assistant: Mapped["Assistant"] = relationship(back_populates="teaching_courses")
    course: Mapped["Course"] = relationship(back_populates="assistant_courses_new")
