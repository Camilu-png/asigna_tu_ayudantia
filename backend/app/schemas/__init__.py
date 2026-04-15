from datetime import time
from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    STUDENT = "student"
    ASSISTANT = "assistant"


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    professor: str = Field(..., min_length=1, max_length=255)
    credits: int = Field(..., ge=0)


class CourseCreate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True


class ScheduleBlockBase(BaseModel):
    day: str = Field(..., min_length=1, max_length=20)
    start_time: str = Field(..., min_length=1, max_length=10)
    end_time: str = Field(..., min_length=1, max_length=10)


class ScheduleBlockCreate(ScheduleBlockBase):
    course_id: int


class ScheduleBlockResponse(ScheduleBlockBase):
    id: int
    course_id: int | None

    class Config:
        from_attributes = True


class CreateScheduleBlockRequest(BaseModel):
    user_id: int
    day: str = Field(..., min_length=1, max_length=20)
    start_time: str = Field(..., min_length=1, max_length=10)
    end_time: str = Field(..., min_length=1, max_length=10)
    course_id: int | None = None
    new_course: CourseCreate | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class ScheduleBlockWithUserResponse(BaseModel):
    id: int
    day: str
    start_time: str
    end_time: str
    course_id: int | None
    course_name: str | None
    course_code: str | None
    color: str | None

    class Config:
        from_attributes = True


class ScheduleConflictError(BaseModel):
    detail: str
    conflicting_block: ScheduleBlockWithUserResponse | None = None
