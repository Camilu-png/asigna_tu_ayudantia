from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.routers import router as api_router
from app.core.config import ALLOWED_ORIGINS
from app.db.session import engine
from app.db.base import Base
from app.models.course import Course
from app.models.student import Student
from app.models.assistant import Assistant
from app.models.assistant_course import AssistantCourse
from app.models.schedule import ScheduleBlock, StudentSchedule, AssistantSchedule

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Asigna Tu Ayudantía API!", "status": "OK"}


app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
