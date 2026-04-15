from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.db.base import Base
from app.models.user_course import UserCourse
from app.models.schedule import UserSchedule


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    user_courses: Mapped[list["UserCourse"]] = relationship(back_populates="user")
    user_schedules: Mapped[list["UserSchedule"]] = relationship(back_populates="user")
