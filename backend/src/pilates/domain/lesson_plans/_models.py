from __future__ import annotations

import datetime as dt
import enum

import pydantic

from pilates.domain import exercises


class LessonPlanSection(enum.StrEnum):
    WARM_UP = "WARM_UP"
    MAIN_SESSION = "MAIN_SESSION"
    COOL_DOWN = "COOL_DOWN"


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
    warm_up: list[ExerciseSequence]
    main_session: list[ExerciseSequence]
    cool_down: list[ExerciseSequence]

    @property
    def exercise_sequences(self) -> list[ExerciseSequence]:
        return self.warm_up + self.main_session + self.cool_down
