from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.assistant import Assistant
from app.models.assistant_course import AssistantCourse
from app.models.course import Course


router = APIRouter(tags=["assistant"])


@router.get("/courses/{assistant_id}")
async def get_assistant_courses(
    assistant_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AssistantCourse)
        .options(selectinload(AssistantCourse.course))
        .where(AssistantCourse.assistant_id == assistant_id)
    )
    assistant_courses = result.scalars().all()

    return {
        "courses": [
            {
                "id": ac.course.id,
                "name": ac.course.name,
                "code": ac.course.code,
                "professor": ac.course.professor,
                "credits": ac.course.credits,
                "color": ac.color,
            }
            for ac in assistant_courses
            if ac.course
        ]
    }


@router.post("/courses/{assistant_id}")
async def add_assistant_course(
    assistant_id: int,
    course_id: int,
    color: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Assistant).where(Assistant.id == assistant_id))
    assistant = result.scalar_one_or_none()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    result = await db.execute(
        select(AssistantCourse).where(
            AssistantCourse.assistant_id == assistant_id,
            AssistantCourse.course_id == course_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already assigned to assistant",
        )

    assistant_course = AssistantCourse(
        assistant_id=assistant_id,
        course_id=course_id,
        color=color or "#aa3bff",
    )
    db.add(assistant_course)
    await db.commit()
    await db.refresh(assistant_course)

    return {
        "id": assistant_course.id,
        "assistant_id": assistant_course.assistant_id,
        "course_id": assistant_course.course_id,
        "color": assistant_course.color,
    }
