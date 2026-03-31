from fastapi import APIRouter
from app.api.v1 import courses, auth, schedule

router = APIRouter()

router.include_router(auth.router)
router.include_router(courses.router, prefix="/courses", tags=["courses"])
router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
