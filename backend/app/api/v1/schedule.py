from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.schedule_service import ScheduleService
from app.schemas import (
    CreateScheduleBlockRequest,
    ScheduleBlockWithUserResponse,
)


router = APIRouter(tags=["schedule"])


@router.post(
    "/blocks",
    response_model=ScheduleBlockWithUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule_block(
    request: CreateScheduleBlockRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    try:
        result = await service.create_schedule_block(request)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el bloque de horario: {str(e)}",
        )


@router.get(
    "/blocks/{user_id}",
    response_model=list[ScheduleBlockWithUserResponse],
)
async def get_user_schedule(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    try:
        result = await service.get_user_schedule(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el horario: {str(e)}",
        )


@router.delete(
    "/blocks/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule_block(
    block_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    try:
        deleted = await service.delete_schedule_block(block_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bloque de horario no encontrado",
            )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el bloque de horario: {str(e)}",
        )
