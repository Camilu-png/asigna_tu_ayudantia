from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.schedule import ScheduleBlock, UserSchedule
from app.models.user import User
from app.models.assistant_help_block import AssistantHelpBlock
from app.schemas import (
    CreateScheduleBlockRequest,
    CourseCreate,
    ScheduleBlockWithUserResponse,
)


class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_schedule_block(
        self, request: CreateScheduleBlockRequest
    ) -> ScheduleBlockWithUserResponse:
        user_id = request.user_id

        course = await self._get_or_create_course(request.course_id, request.new_course)

        await self._validate_no_schedule_conflict(
            user_id, request.day, request.start_time, request.end_time
        )

        schedule_block = ScheduleBlock(
            day=request.day,
            start_time=request.start_time,
            end_time=request.end_time,
            course_id=course.id,
        )
        self.db.add(schedule_block)
        await self.db.flush()

        user_schedule = UserSchedule(
            user_id=user_id,
            schedule_block_id=schedule_block.id,
            color=request.color,
        )
        self.db.add(user_schedule)

        await self.db.flush()
        await self.db.refresh(schedule_block)

        return ScheduleBlockWithUserResponse(
            id=schedule_block.id,
            day=schedule_block.day,
            start_time=schedule_block.start_time,
            end_time=schedule_block.end_time,
            course_id=schedule_block.course_id,
            course_name=course.name if course else None,
            course_code=course.code if course else None,
            color=request.color,
        )

    async def _get_or_create_course(
        self, course_id: int | None, new_course: CourseCreate | None
    ) -> Course:
        if course_id is not None:
            result = await self.db.execute(select(Course).where(Course.id == course_id))
            course = result.scalar_one_or_none()
            if not course:
                raise ValueError(f"Course with id {course_id} not found")
            return course

        if new_course:
            existing = await self._find_existing_course(
                new_course.code, new_course.name
            )
            if existing:
                return existing

            course = Course(
                name=new_course.name,
                code=new_course.code,
                professor=new_course.professor,
                credits=new_course.credits,
            )
            self.db.add(course)
            await self.db.flush()
            return course

        raise ValueError("Either course_id or new_course must be provided")

    async def _find_existing_course(self, code: str, name: str) -> Course | None:
        result = await self.db.execute(
            select(Course).where(or_(Course.code.ilike(code), Course.name.ilike(name)))
        )
        return result.scalar_one_or_none()

    async def _validate_no_schedule_conflict(
        self,
        user_id: int,
        day: str,
        start_time: str,
        end_time: str,
    ):
        result = await self.db.execute(
            select(UserSchedule)
            .join(ScheduleBlock)
            .where(
                and_(
                    UserSchedule.user_id == user_id,
                    ScheduleBlock.day == day,
                    ScheduleBlock.start_time < end_time,
                    ScheduleBlock.end_time > start_time,
                )
            )
        )
        conflict = result.scalars().first()
        if conflict:
            raise ValueError(
                "Ya existe un bloque de horario en este horario. "
                "No puedes tener dos bloques en el mismo horario."
            )

        result = await self.db.execute(
            select(AssistantHelpBlock)
            .join(ScheduleBlock)
            .where(
                and_(
                    AssistantHelpBlock.assistant_id == user_id,
                    ScheduleBlock.day == day,
                    ScheduleBlock.start_time < end_time,
                    ScheduleBlock.end_time > start_time,
                )
            )
        )
        conflict = result.scalars().first()
        if conflict:
            raise ValueError(
                "Ya existe un bloque de ayuda en este horario. "
                "No puedes tener un horario y un bloque de ayuda al mismo tiempo."
            )

    async def get_user_schedule(
        self, user_id: int
    ) -> list[ScheduleBlockWithUserResponse]:
        result = await self.db.execute(
            select(UserSchedule)
            .options(
                selectinload(UserSchedule.schedule_block).selectinload(
                    ScheduleBlock.course
                )
            )
            .where(UserSchedule.user_id == user_id)
        )
        schedules = result.scalars().all()

        result_list = []
        for schedule in schedules:
            block = schedule.schedule_block
            course = block.course if block.course_id else None
            result_list.append(
                ScheduleBlockWithUserResponse(
                    id=block.id,
                    day=block.day,
                    start_time=block.start_time,
                    end_time=block.end_time,
                    course_id=block.course_id,
                    course_name=course.name if course else None,
                    course_code=course.code if course else None,
                    color=schedule.color,
                )
            )

        return result_list

    async def delete_schedule_block(self, block_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(UserSchedule).where(
                and_(
                    UserSchedule.schedule_block_id == block_id,
                    UserSchedule.user_id == user_id,
                )
            )
        )
        schedule = result.scalar_one_or_none()
        if schedule:
            await self.db.delete(schedule)
            block_result = await self.db.execute(
                select(ScheduleBlock).where(ScheduleBlock.id == block_id)
            )
            block = block_result.scalar_one_or_none()
            if block:
                await self.db.delete(block)
            await self.db.commit()
            return True
        return False
