from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.session import get_db
from app.models.course import Course
from app.models.user import User
from app.models.user_course import UserCourse

router = APIRouter()


class UserCourseResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    role: str
    color: str | None


class EnrollRequest(BaseModel):
    course_id: int
    role: str
    color: str | None = None


@router.get("/")
async def get_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course))
    courses = result.scalars().all()
    return {
        "courses": [
            {
                "id": course.id,
                "name": course.name,
                "code": course.code,
                "professor": course.professor,
                "credits": course.credits,
            }
            for course in courses
        ]
    }


@router.get("/{course_id}/students")
async def get_course_students(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserCourse)
        .options(selectinload(UserCourse.user))
        .where(UserCourse.course_id == course_id, UserCourse.role == "STUDENT")
    )
    user_courses = result.scalars().all()
    return {
        "students": [
            {
                "id": uc.user.id,
                "name": uc.user.name,
                "email": uc.user.email,
                "color": uc.color,
            }
            for uc in user_courses
            if uc.user
        ]
    }


@router.get("/{course_id}/assistants")
async def get_course_assistants(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserCourse)
        .options(selectinload(UserCourse.user))
        .where(UserCourse.course_id == course_id, UserCourse.role == "ASSISTANT")
    )
    user_courses = result.scalars().all()
    return {
        "assistants": [
            {
                "id": uc.user.id,
                "name": uc.user.name,
                "email": uc.user.email,
                "color": uc.color,
            }
            for uc in user_courses
            if uc.user
        ]
    }


@router.post("/{user_id}/enroll")
async def enroll_user(
    user_id: int, request: EnrollRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    result = await db.execute(select(Course).where(Course.id == request.course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    if request.role not in ("STUDENT", "ASSISTANT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be STUDENT or ASSISTANT",
        )

    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == request.course_id,
            UserCourse.role == request.role,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already enrolled in this course with this role",
        )

    if request.role == "ASSISTANT":
        result = await db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id, UserCourse.role == "ASSISTANT"
            )
        )
        existing_assistant = result.scalars().all()
        if any(uc.course_id == request.course_id for uc in existing_assistant):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assistant already assigned to this course",
            )

    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == request.course_id,
            UserCourse.role != request.role,
        )
    )
    conflicting = result.scalar_one_or_none()
    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User cannot be both student and assistant in the same course",
        )

    user_course = UserCourse(
        user_id=user_id,
        course_id=request.course_id,
        role=request.role,
        color=request.color,
    )
    db.add(user_course)
    await db.commit()
    await db.refresh(user_course)

    return {
        "id": user_course.id,
        "user_id": user_course.user_id,
        "course_id": user_course.course_id,
        "role": user_course.role,
        "color": user_course.color,
    }


@router.delete("/{user_id}/enroll/{course_id}")
async def unenroll_user(
    user_id: int, course_id: int, role: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id,
            UserCourse.role == role,
        )
    )
    user_course = result.scalar_one_or_none()
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )

    await db.delete(user_course)
    await db.commit()

    return {"message": "Successfully unenrolled"}
