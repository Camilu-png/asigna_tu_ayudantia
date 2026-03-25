from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey
from app.db.base import Base

class SolverRun(Base):
    __tablename__ = "solutions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    executed_by: Mapped[int] = mapped_column(Integer, ForeignKey("assistants.id"), nullable=False)
