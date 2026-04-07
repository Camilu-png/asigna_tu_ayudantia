import numpy as np
from dataclasses import dataclass
from typing import Callable


@dataclass
class ScheduleData:
    blocks: np.ndarray
    assistants: np.ndarray
    availability: np.ndarray
    num_slots: int
    num_days: int
    num_assistants: int

    @property
    def block_ids(self) -> np.ndarray:
        return self.blocks[:, 0]

    @property
    def days(self) -> np.ndarray:
        return self.blocks[:, 1]

    @property
    def slot_indices(self) -> np.ndarray:
        return self.blocks[:, 2]


class Solution:
    def __init__(self, data: ScheduleData):
        self.data = data
        self.X = np.zeros(
            (data.num_slots, data.num_days, data.num_assistants), dtype=int
        )

    def copy(self):
        new_solution = Solution(self.data)
        new_solution.X = self.X.copy()
        return new_solution

    def assign(self, slot: int, day: int, assistant: int):
        self.X[slot, day, assistant] = 1

    def unassign(self, slot: int, day: int, assistant: int):
        self.X[slot, day, assistant] = 0

    def is_assigned(self, slot: int, day: int) -> bool:
        return self.X[slot, day, :].any()

    def is_assigned_to(self, slot: int, day: int, assistant: int) -> bool:
        return self.X[slot, day, assistant] == 1

    def assistants_in_slot(self, slot: int, day: int) -> np.ndarray:
        return np.where(self.X[slot, day, :] == 1)[0]

    def is_available(self, slot: int, day: int, assistant: int) -> bool:
        return self.data.availability[slot, day, assistant] == 0

    def has_overlap(self, assistant: int, slot: int, day: int) -> bool:
        for s in range(self.data.num_slots):
            if s != slot and self.X[s, day, assistant] == 1:
                return True
        return False

    def occupied_slots(self) -> list[tuple[int, int, int]]:
        occupied = []
        for slot in range(self.data.num_slots):
            for day in range(self.data.num_days):
                for assistant in range(self.data.num_assistants):
                    if self.X[slot, day, assistant] == 1:
                        occupied.append((slot, day, assistant))
        return occupied

    def free_slots_for(self, assistant: int) -> list[tuple[int, int]]:
        free = []
        for slot in range(self.data.num_slots):
            for day in range(self.data.num_days):
                if self.is_available(slot, day, assistant):
                    if not self.is_assigned(slot, day):
                        free.append((slot, day))
        return free


def validate_solution(solution: Solution) -> tuple[bool, str]:
    for slot in range(solution.data.num_slots):
        for day in range(solution.data.num_days):
            if solution.is_assigned(slot, day):
                assistants = solution.assistants_in_slot(slot, day)
                if len(assistants) > 1:
                    return False, f"More than one assistant in slot {slot}, day {day}"

                assistant = assistants[0]
                if not solution.is_available(slot, day, assistant):
                    return (
                        False,
                        f"Assistant {assistant} unavailable for slot {slot}, day {day}",
                    )

                if solution.has_overlap(assistant, slot, day):
                    return (
                        False,
                        f"Assistant {assistant} has overlap on slot {slot}, day {day}",
                    )

    return True, "Solution is valid"


def fitness(solution: Solution, data: ScheduleData) -> float:
    fitness_count = 0.0

    for slot in range(data.num_slots):
        for day in range(data.num_days):
            if solution.is_assigned(slot, day):
                fitness_count += 1.0

                if data.days[slot] == "Friday":
                    fitness_count -= 0.3

    return fitness_count


def random_move(solution: Solution) -> Solution:
    import random

    new_solution = solution.copy()
    occupied = new_solution.occupied_slots()

    if not occupied:
        return new_solution

    move_type = random.choice(["unassign", "shift", "swap"])

    if move_type == "unassign":
        slot, day, assistant = random.choice(occupied)
        new_solution.unassign(slot, day, assistant)

    elif move_type == "shift":
        slot, day, assistant = random.choice(occupied)
        free_slots = new_solution.free_slots_for(assistant)
        if free_slots:
            new_slot, new_day = random.choice(free_slots)
            new_solution.unassign(slot, day, assistant)
            new_solution.assign(new_slot, new_day, assistant)

    else:
        if len(occupied) >= 2:
            (s1, d1, a1), (s2, d2, a2) = random.sample(occupied, 2)
            new_solution.unassign(s1, d1, a1)
            new_solution.unassign(s2, d2, a2)
            new_solution.assign(s2, d2, a1)
            new_solution.assign(s1, d1, a2)

    return new_solution


def simulated_annealing(
    solution: Solution,
    initial_temp: float = 100.0,
    final_temp: float = 0.01,
    alpha: float = 0.995,
    max_iter: int = 5000,
    fitness_fn: Callable[[Solution, ScheduleData], float] = fitness,
) -> Solution:
    current_solution = solution
    current_fitness = fitness_fn(current_solution, solution.data)
    best_solution = current_solution
    best_fitness = current_fitness
    temperature = initial_temp

    iteration = 0
    while temperature > final_temp and iteration < max_iter:
        new_solution = random_move(current_solution)

        valid, _ = validate_solution(new_solution)
        if not valid:
            new_fitness = float("-inf")
        else:
            new_fitness = fitness_fn(new_solution, new_solution.data)

        delta_fitness = new_fitness - current_fitness

        if delta_fitness > 0 or np.exp(delta_fitness / temperature) >= np.random.rand():
            current_solution = new_solution
            current_fitness = new_fitness

            if current_fitness > best_fitness:
                best_solution = current_solution
                best_fitness = current_fitness

        temperature *= alpha
        iteration += 1

    print(f"Iterations: {iteration}, Best fitness: {best_fitness}")
    return best_solution
