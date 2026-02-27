"""
Schemas used to generate API responses.
"""

import datetime as dt
import typing

import pydantic

from pilates.domain import exercises, lesson_plans


class Exercise(exercises.Exercise):
    # No deviation from domain model.
    pass

    @classmethod
    def from_domain(cls, obj: exercises.Exercise) -> typing.Self:
        return cls(**obj.model_dump())


class ExerciseSet(pydantic.BaseModel):
    id: int
    # Has a fully hydrated exercise, rather than just an `exercise_id`.
    exercise: Exercise
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    equipment_variant: list[exercises.Equipment]

    @classmethod
    def from_domain(
        cls,
        obj: lesson_plans.ExerciseSet,
        *,
        exercises_by_id: dict[int, exercises.Exercise],
    ) -> typing.Self:
        exercise = exercises_by_id[obj.exercise_id]
        return cls(
            id=obj.id,
            exercise=Exercise.from_domain(obj=exercise),
            reps=obj.reps,
            duration_seconds=obj.duration_seconds,
            movement_variant=obj.movement_variant,
            equipment_variant=obj.equipment_variant,
        )


class ExerciseSequence(pydantic.BaseModel):
    id: int
    name: str
    sets: list[ExerciseSet]
    reps: int
    notes: str

    @classmethod
    def from_domain(
        cls,
        obj: lesson_plans.ExerciseSequence,
        *,
        exercises_by_id: dict[int, exercises.Exercise],
    ) -> typing.Self:
        return cls(
            id=obj.id,
            name=obj.name,
            sets=[
                ExerciseSet.from_domain(obj=set_obj, exercises_by_id=exercises_by_id)
                for set_obj in obj.sets
            ],
            reps=obj.reps,
            notes=obj.notes,
        )


class LessonPlan(pydantic.BaseModel):
    id: int
    name: str
    description: str
    date: dt.date
    warm_up: list[ExerciseSequence]
    main_session: list[ExerciseSequence]
    cool_down: list[ExerciseSequence]

    @classmethod
    def from_domain(
        cls,
        obj: lesson_plans.LessonPlan,
        *,
        exercises_by_id: dict[int, exercises.Exercise],
    ) -> typing.Self:
        return cls(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            date=obj.date,
            warm_up=[
                ExerciseSequence.from_domain(obj=seq, exercises_by_id=exercises_by_id)
                for seq in obj.warm_up
            ],
            main_session=[
                ExerciseSequence.from_domain(obj=seq, exercises_by_id=exercises_by_id)
                for seq in obj.main_session
            ],
            cool_down=[
                ExerciseSequence.from_domain(obj=seq, exercises_by_id=exercises_by_id)
                for seq in obj.cool_down
            ],
        )
