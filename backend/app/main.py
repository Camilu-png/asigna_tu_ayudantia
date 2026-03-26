from fastapi import FastAPI
from app.api.v1.routers import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.core.config import ALLOWED_ORIGINS
from app.models.course import Course
from app.models.student import Student
from app.models.assistant import Assistant
from app.models.time_block import TimeBlock
from app.models.student_course import StudentCourse, AssistantCourse
from app.models.solver_run import SolverRun

app = FastAPI()
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
