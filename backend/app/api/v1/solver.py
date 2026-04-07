from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.solver_service import SolverService


router = APIRouter(tags=["solver"])


class SolveRequest(BaseModel):
    course_id: int
    save: bool = False


class SolveResponse(BaseModel):
    success: bool
    message: str
    assignments: list[dict] = []
    fitness: float = 0.0


@router.post("/solve", response_model=SolveResponse)
async def run_solver(request: SolveRequest, db: AsyncSession = Depends(get_db)):
    service = SolverService(db)
    result = await service.run_solver(request.course_id)

    if result["success"] and request.save:
        await service.save_solution(request.course_id, result["assignments"])

    return result
