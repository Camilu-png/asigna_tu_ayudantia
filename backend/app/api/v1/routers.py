from fastapi import APIRouter
from app.api.v1 import courses, auth, schedule, assistant, solver, admin

router = APIRouter()

router.include_router(auth.router)
router.include_router(courses.router, prefix="/courses", tags=["courses"])
router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
router.include_router(solver.router, prefix="/solver", tags=["solver"])
router.include_router(admin.router)
