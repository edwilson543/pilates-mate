from __future__ import annotations

import datetime as dt
import enum

import pydantic


class Difficulty(enum.StrEnum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class MuscleGroup(enum.StrEnum):
    CORE = "CORE"
    GLUTES = "GLUTES"
    HIP_FLEXORS = "HIP_FLEXORS"
    BACK_EXTENSORS = "BACK_EXTENSORS"
    SHOULDERS = "SHOULDERS"
    INNER_THIGHS = "INNER_THIGHS"
    HAMSTRINGS = "HAMSTRINGS"
    OBLIQUES = "OBLIQUES"
    TRICEPS = "TRICEPS"
    CHEST = "CHEST"


class StartingPosition(enum.StrEnum):
    SUPINE = "SUPINE"
    PRONE = "PRONE"
    SIDE_LYING = "SIDE_LYING"
    SEATED = "SEATED"
    QUADRUPED = "QUADRUPED"
    STANDING = "STANDING"
    KNEELING = "KNEELING"
    PLANK = "PLANK"
    SIDE_KNEELING = "SIDE_KNEELING"


class Exercise(pydantic.BaseModel):
    id: int
    name: str
    description: str
    difficulty: Difficulty
    primary_muscle_group: MuscleGroup
    starting_position: StartingPosition


class ExerciseSet(pydantic.BaseModel):
    exercise: Exercise
    reps: int
    duration_seconds: int


class ExerciseSequence(pydantic.BaseModel):
    name: str
    notes: str
    sets: list[ExerciseSet]

    @property
    def duration_seconds(self) -> int:
        return sum(set_.duration_seconds for set_ in self.sets)


class LessonPlan(pydantic.BaseModel):
    id: int
    name: str
    description: str
    date: dt.date
    warm_up: list[ExerciseSequence]
    main_session: list[ExerciseSequence]
    cool_down: list[ExerciseSequence]
