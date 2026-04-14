import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schedule import ScheduleBlock, AssistantSchedule
from app.models.assistant import Assistant
from app.models.assistant_help_block import AssistantHelpBlock
from app.models.constants import DAY_MAP
from app.services.simulated_annealing import (
    ScheduleData,
    Solution,
    simulated_annealing,
    validate_solution,
    fitness,
)


class SolverService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_schedule_data(self, course_id: int) -> ScheduleData:
        result = await self.db.execute(
            select(ScheduleBlock)
            .options(selectinload(ScheduleBlock.course))
            .where(ScheduleBlock.course_id == course_id)
            .order_by(ScheduleBlock.day, ScheduleBlock.start_time)
        )
        course_blocks = result.scalars().all()

        if not course_blocks:
            raise ValueError(f"No schedule blocks found for course {course_id}")

        result = await self.db.execute(select(Assistant))
        assistants = result.scalars().all()

        result = await self.db.execute(
            select(AssistantSchedule).options(
                selectinload(AssistantSchedule.schedule_block)
            )
        )
        existing_schedules = result.scalars().all()

        unique_days = sorted(
            set(b.day for b in course_blocks), key=lambda d: DAY_MAP.get(d, 0)
        )
        unique_days = [d for d in DAY_MAP.keys() if d in unique_days]

        sorted_blocks = sorted(
            course_blocks, key=lambda b: (DAY_MAP.get(b.day, 0), b.start_time)
        )
        block_ids = [b.id for b in sorted_blocks]

        num_slots = len(sorted_blocks)
        num_days = len(unique_days)
        num_assistants = len(assistants)

        assistant_map = {a.id: idx for idx, a in enumerate(assistants)}

        blocks_array = np.zeros((num_slots, 3), dtype=int)
        for idx, block in enumerate(sorted_blocks):
            day_idx = unique_days.index(block.day)
            blocks_array[idx] = [block.id, day_idx, idx]

        availability = np.zeros((num_slots, num_days, num_assistants), dtype=int)

        for sched in existing_schedules:
            if sched.schedule_block_id in block_ids:
                block_idx = block_ids.index(sched.schedule_block_id)
                assistant_idx = assistant_map.get(sched.assistant_id)
                if assistant_idx is not None:
                    day_idx = unique_days.index(sched.schedule_block.day)
                    availability[block_idx, day_idx, assistant_idx] = 1

        return ScheduleData(
            blocks=blocks_array,
            assistants=np.arange(num_assistants),
            availability=availability,
            num_slots=num_slots,
            num_days=num_days,
            num_assistants=num_assistants,
        )

    async def run_solver(self, course_id: int) -> dict:
        data = await self.get_schedule_data(course_id)

        if data.num_assistants == 0 or data.num_slots == 0:
            return {"success": False, "message": "No assistants or blocks available"}

        solution = Solution(data)

        assistants_assigned_today = {}

        for slot in range(data.num_slots):
            for day in range(data.num_days):
                if solution.is_assigned(slot, day):
                    continue

                used_today = assistants_assigned_today.get(day, set())

                for assistant in range(data.num_assistants):
                    if assistant in used_today:
                        continue
                    if solution.is_available(slot, day, assistant):
                        solution.assign(slot, day, assistant)
                        assistants_assigned_today.setdefault(day, set()).add(assistant)
                        break

        result = simulated_annealing(
            solution=solution,
            initial_temp=100.0,
            final_temp=0.01,
            alpha=0.995,
            max_iter=3000,
            fitness_fn=fitness,
        )

        valid, message = validate_solution(result)
        if not valid:
            return {"success": False, "message": f"Invalid solution: {message}"}

        result_assistants = await self.db.execute(select(Assistant))
        assistant_ids = [a.id for a in result_assistants.scalars().all()]
        assistant_map = {idx: aid for idx, aid in enumerate(assistant_ids)}

        assignments = []
        for slot in range(result.data.num_slots):
            for day in range(result.data.num_days):
                for assistant in range(result.data.num_assistants):
                    if result.X[slot, day, assistant] == 1:
                        block_id = int(result.data.blocks[slot, 0])
                        assistant_id = int(assistant_map[assistant])
                        assignments.append(
                            {
                                "block_id": block_id,
                                "assistant_id": assistant_id,
                            }
                        )

        return {
            "success": True,
            "message": "Solution found",
            "assignments": assignments,
            "fitness": float(fitness(result, data)),
        }

    async def save_solution(self, course_id: int, assignments: list[dict]) -> dict:
        for assignment in assignments:
            existing = await self.db.execute(
                select(AssistantHelpBlock).where(
                    AssistantHelpBlock.schedule_block_id == assignment["block_id"],
                    AssistantHelpBlock.course_id == course_id,
                )
            )
            if existing.scalar_one_or_none():
                continue

            help_block = AssistantHelpBlock(
                assistant_id=assignment["assistant_id"],
                schedule_block_id=assignment["block_id"],
                course_id=course_id,
            )
            self.db.add(help_block)

        await self.db.commit()
        return {"success": True, "message": "Solution saved"}
