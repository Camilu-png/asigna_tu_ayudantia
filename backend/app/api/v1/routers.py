from fastapi import APIRouter
from app.api.v1 import courses

router = APIRouter()

router.include_router(courses.router, prefix="/courses", tags=["courses"])