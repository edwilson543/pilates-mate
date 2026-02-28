from __future__ import annotations

import enum

import pydantic


class Difficulty(enum.StrEnum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class Equipment(enum.StrEnum):
    BALL = "BALL"
    BAND = "BAND"
    RING = "RING"
    ANKLE_WEIGHTS = "ANKLE_WEIGHTS"
    HAND_WEIGHTS = "HAND_WEIGHTS"


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


class MovementVariant(enum.StrEnum):
    STANDARD = "STANDARD"
    PULSE = "PULSE"
    HOLD = "HOLD"


class Exercise(pydantic.BaseModel):
    id: int
    name: str
    description: str
    category: ExerciseCategory
    difficulty: Difficulty
    primary_muscle_group: MuscleGroup
    starting_position: StartingPosition
    movement_variants: list[MovementVariant]
    equipment_variants: list[Equipment]
