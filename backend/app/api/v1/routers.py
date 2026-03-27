from fastapi import APIRouter
from app.api.v1 import courses
from app.api.v1 import auth

router = APIRouter()

router.include_router(auth.router)
router.include_router(courses.router, prefix="/courses", tags=["courses"])
