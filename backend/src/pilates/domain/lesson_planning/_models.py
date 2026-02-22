from __future__ import annotations

import datetime as dt
import enum

import pydantic


class Difficulty(enum.StrEnum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class Equipment(enum.StrEnum):
    BALL = "BALL"
    ANKLE_WEIGHTS = "ANKLE_WEIGHTS"


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


class ExerciseCategory(enum.StrEnum):
    BREATH_WORK = "BREATH_WORK"
    STRETCH = "STRETCH"
    MOBILITY = "MOBILITY"
    EFFORT = "EFFORT"


class ExerciseVariant(enum.StrEnum):
    STANDARD = "STANDARD"
    PULSE = "PULSE"
    HOLD = "HOLD"


class LessonPlanSection(enum.StrEnum):
    WARM_UP = "WARM_UP"
    MAIN_SESSION = "MAIN_SESSION"
    COOL_DOWN = "COOL_DOWN"


class Exercise(pydantic.BaseModel):
    id: int
    name: str
    description: str
    category: ExerciseCategory
    difficulty: Difficulty
    primary_muscle_group: MuscleGroup
    starting_position: StartingPosition
    variants: list[ExerciseVariant]


class ExerciseSet(pydantic.BaseModel):
    id: int
    exercise: Exercise
    reps: int
    duration_seconds: int
    variant: ExerciseVariant


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

    @property
    def exercises(self) -> list[Exercise]:
        return [
            exercise_set.exercise
            for exercise_sequence in self.exercise_sequences
            for exercise_set in exercise_sequence.sets
        ]
