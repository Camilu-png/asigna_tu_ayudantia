from fastapi import FastAPI
from app.api.v1.routers import router as api_router
from app.db.session import engine
from app.db.base import Base
from app.models import *

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Asigna Tu Ayudantía API!", "status": "OK"}

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)