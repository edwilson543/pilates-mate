import typing

import fastapi
import pydantic

from pilates import config
from pilates.application import (
    create_empty_lesson_plan_with_requirements,
    generate_lesson_plan,
)
from pilates.domain import exercises, lesson_plans, utils
from pilates.interfaces.api import dependencies, schemas


router = fastapi.APIRouter()


class CreateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: exercises.ExerciseCategory
    difficulty: exercises.Difficulty
    primary_muscle_group: exercises.MuscleGroup
    starting_position: exercises.StartingPosition
    movement_variants: list[exercises.MovementVariant]


class CreateExerciseResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: exercises.ExerciseCategory
    difficulty: exercises.Difficulty
    primary_muscle_group: exercises.MuscleGroup
    starting_position: exercises.StartingPosition
    movement_variants: list[exercises.MovementVariant]


class GenerateLessonPlanRequest(pydantic.BaseModel):
    requirements: lesson_plans.LessonPlanRequirements


class GenerateLessonPlanResponse(pydantic.BaseModel):
    id: int


@router.post("/", status_code=201)
async def generate_lesson_plan_(
    request: typing.Annotated[GenerateLessonPlanRequest, fastapi.Body()],
    background_tasks: fastapi.BackgroundTasks,
    settings: dependencies.SettingsT,
    uow: dependencies.UnitOfWorkT,
) -> GenerateLessonPlanResponse:
    created_at = utils.now().date()
    lesson_plan_id = await create_empty_lesson_plan_with_requirements.create_empty_lesson_plan_with_requirements(
        created_at=created_at,
        requirements=request.requirements,
        uow=uow,
    )

    client = config.get_completion_client(settings)
    background_tasks.add_task(
        generate_lesson_plan.generate_lesson_plan,
        lesson_plan_id=lesson_plan_id,
        client=client,
        uow=uow,
    )

    return GenerateLessonPlanResponse(id=lesson_plan_id)


@router.get("/")
async def get_lesson_plans(uow: dependencies.UnitOfWorkT) -> list[schemas.LessonPlan]:
    all_plans = uow.lesson_plans.get_lesson_plans()
    all_exercises = uow.exercises.get_exercises()
    exercises_by_id = {ex.id: ex for ex in all_exercises}
    return [
        schemas.LessonPlan.from_domain(plan, exercises_by_id=exercises_by_id)
        for plan in all_plans
    ]


@router.get("/{lesson_plan_id}")
async def get_lesson_plan(
    lesson_plan_id: int, uow: dependencies.UnitOfWorkT
) -> schemas.LessonPlan:
    try:
        lesson_plan = uow.lesson_plans.get_lesson_plan(lesson_plan_id)
        all_exercises = uow.exercises.get_exercises()
        exercises_by_id = {ex.id: ex for ex in all_exercises}
        return schemas.LessonPlan.from_domain(
            lesson_plan, exercises_by_id=exercises_by_id
        )
    except lesson_plans.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


@router.delete("/{lesson_plan_id}", status_code=204)
async def delete_lesson_plan(
    lesson_plan_id: int, uow: dependencies.UnitOfWorkT
) -> None:
    try:
        uow.lesson_plans.delete_lesson_plan(lesson_plan_id)
    except lesson_plans.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


class AddSetToSequenceRequest(pydantic.BaseModel):
    exercise_id: int
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    equipment_variant: list[exercises.Equipment]


class AddSetToSequenceResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseSetRequest(pydantic.BaseModel):
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    equipment_variant: list[exercises.Equipment]


@router.post("/sequences/{sequence_id}/sets", status_code=201)
async def add_set_to_sequence(
    sequence_id: int,
    request: typing.Annotated[AddSetToSequenceRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> AddSetToSequenceResponse:
    try:
        set_id = uow.lesson_plans.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=request.exercise_id,
            reps=request.reps,
            duration_seconds=request.duration_seconds,
            movement_variant=request.movement_variant,
            equipment_variant=request.equipment_variant,
        )
        return AddSetToSequenceResponse(id=set_id)
    except lesson_plans.SequenceDoesNotExist:
        raise fastapi.HTTPException(
            status_code=404, detail="Exercise sequence not found."
        )
    except exercises.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@router.put("/sequences/{sequence_id}/sets/{set_id}", status_code=204)
async def update_exercise_set(
    sequence_id: int,
    set_id: int,
    request: typing.Annotated[UpdateExerciseSetRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> None:
    try:
        uow.lesson_plans.update_exercise_set(
            id=set_id,
            reps=request.reps,
            duration_seconds=request.duration_seconds,
            movement_variant=request.movement_variant,
            equipment_variant=request.equipment_variant,
        )
    except lesson_plans.SetDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Set not found.")


@router.delete("/sequences/{sequence_id}/sets/{set_id}", status_code=204)
async def delete_exercise_set(
    sequence_id: int, set_id: int, uow: dependencies.UnitOfWorkT
) -> None:
    try:
        uow.lesson_plans.delete_exercise_set(set_id)
    except lesson_plans.SetDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Set not found.")


class AddSequenceToSectionRequest(pydantic.BaseModel):
    section: lesson_plans.LessonPlanSection
    name: str = pydantic.Field(min_length=1, max_length=200)
    reps: int = pydantic.Field(ge=1)
    notes: str = pydantic.Field(max_length=1000)


class AddSequenceToSectionResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseSequenceRequest(pydantic.BaseModel):
    name: str = pydantic.Field(min_length=1, max_length=200)
    reps: int = pydantic.Field(ge=1)
    notes: str = pydantic.Field(max_length=1000)


@router.post("/{lesson_plan_id}/sequences", status_code=201)
async def add_sequence_to_section(
    lesson_plan_id: int,
    request: typing.Annotated[AddSequenceToSectionRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> AddSequenceToSectionResponse:
    try:
        sequence_id = uow.lesson_plans.add_sequence_to_section(
            lesson_plan_id=lesson_plan_id,
            section=request.section,
            name=request.name,
            reps=request.reps,
            notes=request.notes,
        )
        return AddSequenceToSectionResponse(id=sequence_id)
    except lesson_plans.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


@router.put("/sequences/{sequence_id}", status_code=204)
async def update_exercise_sequence(
    sequence_id: int,
    request: typing.Annotated[UpdateExerciseSequenceRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> None:
    try:
        uow.lesson_plans.update_exercise_sequence(
            id=sequence_id,
            name=request.name,
            reps=request.reps,
            notes=request.notes,
        )
    except lesson_plans.SequenceDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Sequence not found.")


@router.delete("/sequences/{sequence_id}", status_code=204)
async def delete_exercise_sequence(
    sequence_id: int, uow: dependencies.UnitOfWorkT
) -> None:
    try:
        uow.lesson_plans.delete_exercise_sequence(sequence_id)
    except lesson_plans.SequenceDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Sequence not found.")
