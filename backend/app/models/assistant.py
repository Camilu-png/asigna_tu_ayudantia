from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.db.base import Base
from app.models.schedule import AssistantSchedule


class Assistant(Base):
    __tablename__ = "assistants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    assistant_schedules: Mapped[list["AssistantSchedule"]] = relationship(
        back_populates="assistant"
    )
