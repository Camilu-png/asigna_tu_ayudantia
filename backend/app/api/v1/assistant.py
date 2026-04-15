from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.user_course import UserCourse
from app.models.course import Course
from app.models.schedule import ScheduleBlock
from app.models.assistant_help_block import AssistantHelpBlock
from app.api.v1.auth import get_current_user, get_current_admin, UserResponse

router = APIRouter(tags=["assistant"])


class AssistantHelpBlockCreate(BaseModel):
    schedule_block_id: int
    course_id: int
    color: str | None = None


@router.get("/{user_id}/courses")
async def get_assistant_courses(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own courses",
        )

    result = await db.execute(
        select(UserCourse)
        .options(selectinload(UserCourse.course))
        .where(UserCourse.user_id == user_id, UserCourse.role == "ASSISTANT")
    )
    user_courses = result.scalars().all()

    return {
        "courses": [
            {
                "id": uc.course.id,
                "name": uc.course.name,
                "code": uc.course.code,
                "professor": uc.course.professor,
                "credits": uc.course.credits,
                "color": uc.color,
            }
            for uc in user_courses
            if uc.course
        ]
    }


@router.get("/{user_id}/help-blocks")
async def get_assistant_help_blocks(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own help blocks",
        )

    result = await db.execute(
        select(AssistantHelpBlock)
        .options(
            selectinload(AssistantHelpBlock.schedule_block),
            selectinload(AssistantHelpBlock.course),
        )
        .where(AssistantHelpBlock.assistant_id == user_id)
    )
    help_blocks = result.scalars().all()

    return {
        "help_blocks": [
            {
                "id": hb.id,
                "schedule_block_id": hb.schedule_block_id,
                "day": hb.schedule_block.day if hb.schedule_block else None,
                "start_time": hb.schedule_block.start_time
                if hb.schedule_block
                else None,
                "end_time": hb.schedule_block.end_time if hb.schedule_block else None,
                "course_id": hb.course_id,
                "course_name": hb.course.name if hb.course else None,
                "color": hb.color,
            }
            for hb in help_blocks
        ]
    }


@router.post("/{user_id}/help-blocks")
async def add_assistant_help_block(
    user_id: int,
    request: AssistantHelpBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own help blocks",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(
        select(ScheduleBlock).where(ScheduleBlock.id == request.schedule_block_id)
    )
    schedule_block = result.scalar_one_or_none()
    if not schedule_block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule block not found",
        )

    result = await db.execute(select(Course).where(Course.id == request.course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == request.course_id,
            UserCourse.role == "ASSISTANT",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an assistant for this course",
        )

    result = await db.execute(
        select(AssistantHelpBlock).where(
            and_(
                AssistantHelpBlock.assistant_id == user_id,
                AssistantHelpBlock.schedule_block_id == request.schedule_block_id,
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assistant already has a help block at this time",
        )

    help_block = AssistantHelpBlock(
        assistant_id=user_id,
        schedule_block_id=request.schedule_block_id,
        course_id=request.course_id,
        color=request.color,
    )
    db.add(help_block)
    await db.commit()
    await db.refresh(help_block)

    return {
        "id": help_block.id,
        "assistant_id": help_block.assistant_id,
        "schedule_block_id": help_block.schedule_block_id,
        "course_id": help_block.course_id,
        "color": help_block.color,
    }


@router.delete("/{user_id}/help-blocks/{help_block_id}")
async def delete_assistant_help_block(
    user_id: int,
    help_block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own help blocks",
        )

    result = await db.execute(
        select(AssistantHelpBlock).where(
            AssistantHelpBlock.id == help_block_id,
            AssistantHelpBlock.assistant_id == user_id,
        )
    )
    help_block = result.scalar_one_or_none()
    if not help_block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help block not found",
        )

    await db.delete(help_block)
    await db.commit()

    return {"message": "Help block deleted successfully"}
