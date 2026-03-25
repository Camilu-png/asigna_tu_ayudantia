from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.course import Course

router = APIRouter()

@router.get("/")
async def get_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course))
    courses = result.scalars().all()
    return {"courses": [
        {
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "proffessor": course.proffessor,
            "credits": course.credits
        }
        for course in courses
    ]}
