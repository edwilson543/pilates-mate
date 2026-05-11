from __future__ import annotations

import datetime as dt
import enum

import pydantic

from pilates.domain import exercises


class LessonPlanSection(enum.StrEnum):
    WARM_UP = "WARM_UP"
    MAIN_SESSION = "MAIN_SESSION"
    COOL_DOWN = "COOL_DOWN"


class LessonPlanStatus(enum.StrEnum):
    PENDING_GENERATION = "PENDING_GENERATION"
    GENERATED = "GENERATED"
    ERRORED = "ERRORED"


class LessonPlanRequirements(pydantic.BaseModel):
    duration_minutes: int
    target_difficulty: exercises.Difficulty
    target_muscle_groups: list[exercises.MuscleGroup]
    example_lesson_plan_ids: list[int] = []
    available_equipment: list[exercises.Equipment]
    user_prompt: str


class ExerciseSet(pydantic.BaseModel):
    id: int
    exercise_id: int
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    # An empty list corresponds to no equipment.
    equipment_variant: list[exercises.Equipment]


class ExerciseSequence(pydantic.BaseModel):
    id: int
    name: str
    sets: list[ExerciseSet]
    reps: int
    notes: str


class LessonPlan(pydantic.BaseModel):
    id: int
    name: str
    description: str
    date: dt.date
    requirements: LessonPlanRequirements
    status: LessonPlanStatus
    warm_up: list[ExerciseSequence]
    main_session: list[ExerciseSequence]
    cool_down: list[ExerciseSequence]

    @property
    def exercise_sequences(self) -> list[ExerciseSequence]:
        return self.warm_up + self.main_session + self.cool_down

    @property
    def exercise_sets(self) -> list[ExerciseSet]:
        return [set for sequence in self.exercise_sequences for set in sequence.sets]
