from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from app.core.security import hash_password as get_password_hash

from app.db.session import get_db
from app.models.user import User
from app.models.course import Course
from app.models.user_course import UserCourse
from app.models.assistant_help_block import AssistantHelpBlock
from app.api.v1.auth import get_current_admin, UserResponse


router = APIRouter(prefix="/admin", tags=["admin"])


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "USER"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class AssignAssistantRequest(BaseModel):
    user_id: int
    color: Optional[str] = None


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(select(User))
    users = result.scalars().all()

    result = await db.execute(select(Course))
    courses = result.scalars().all()

    result = await db.execute(
        select(UserCourse).options(
            selectinload(UserCourse.user), selectinload(UserCourse.course)
        )
    )
    user_courses = result.scalars().all()

    result = await db.execute(
        select(AssistantHelpBlock).options(
            selectinload(AssistantHelpBlock.assistant),
            selectinload(AssistantHelpBlock.course),
        )
    )
    help_blocks = result.scalars().all()

    students_count = sum(1 for uc in user_courses if uc.role == "STUDENT")
    assistants_count = sum(1 for uc in user_courses if uc.role == "ASSISTANT")

    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
            }
            for u in users
        ],
        "courses": [
            {
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "professor": c.professor,
                "credits": c.credits,
            }
            for c in courses
        ],
        "enrollments": [
            {
                "user_id": uc.user_id,
                "user_name": uc.user.name,
                "course_id": uc.course_id,
                "course_name": uc.course.name,
                "role": uc.role,
                "color": uc.color,
            }
            for uc in user_courses
            if uc.user and uc.course
        ],
        "help_blocks": [
            {
                "id": hb.id,
                "assistant_id": hb.assistant_id,
                "assistant_name": hb.assistant.name,
                "course_id": hb.course_id,
                "course_name": hb.course.name,
                "color": hb.color,
            }
            for hb in help_blocks
            if hb.assistant and hb.course
        ],
        "stats": {
            "total_users": len(users),
            "total_courses": len(courses),
            "total_students": students_count,
            "total_assistants": assistants_count,
        },
    }


@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
            }
            for u in users
        ]
    }


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    if user_data.role not in ["USER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be USER or ADMIN",
        )

    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = user_data.email

    if user_data.name:
        user.name = user_data.name

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin users",
        )

    await db.execute(select(UserCourse).where(UserCourse.user_id == user_id))

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}


@router.post("/courses/{course_id}/assign-assistant")
async def assign_assistant(
    course_id: int,
    request: AssignAssistantRequest,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign admin as assistant",
        )

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == request.user_id,
            UserCourse.course_id == course_id,
        )
    )
    existing_enrollment = result.scalar_one_or_none()

    if existing_enrollment:
        if existing_enrollment.role == "ASSISTANT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an assistant in this course",
            )
        existing_enrollment.role = "ASSISTANT"
        if request.color:
            existing_enrollment.color = request.color
        await db.commit()
        await db.refresh(existing_enrollment)
        return {
            "id": existing_enrollment.id,
            "user_id": existing_enrollment.user_id,
            "course_id": existing_enrollment.course_id,
            "role": existing_enrollment.role,
            "color": existing_enrollment.color,
        }

    user_course = UserCourse(
        user_id=request.user_id,
        course_id=course_id,
        role="ASSISTANT",
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


@router.delete("/courses/{course_id}/remove-assistant/{user_id}")
async def remove_assistant(
    course_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin),
):
    result = await db.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id,
            UserCourse.role == "ASSISTANT",
        )
    )
    user_course = result.scalar_one_or_none()
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not an assistant in this course",
        )

    await db.execute(
        select(AssistantHelpBlock).where(
            AssistantHelpBlock.assistant_id == user_id,
            AssistantHelpBlock.course_id == course_id,
        )
    )

    await db.delete(user_course)
    await db.commit()

    return {"message": "Assistant removed from course"}
