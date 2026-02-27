import typing

import fastapi
import pydantic

from pilates import config
from pilates.application import generate_lesson_plan
from pilates.domain import lesson_plans


router = fastapi.APIRouter()


class CreateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: lesson_plans.ExerciseCategory
    difficulty: lesson_plans.Difficulty
    primary_muscle_group: lesson_plans.MuscleGroup
    starting_position: lesson_plans.StartingPosition
    movement_variants: list[lesson_plans.MovementVariant]


class CreateExerciseResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: lesson_plans.ExerciseCategory
    difficulty: lesson_plans.Difficulty
    primary_muscle_group: lesson_plans.MuscleGroup
    starting_position: lesson_plans.StartingPosition
    movement_variants: list[lesson_plans.MovementVariant]


class GenerateLessonPlanRequest(pydantic.BaseModel):
    requirements: generate_lesson_plan.LessonPlanRequirements


class GenerateLessonPlanResponse(pydantic.BaseModel):
    lesson_plan: lesson_plans.LessonPlan


@router.post("/", status_code=201)
async def generate_lesson_plan_(
    request: typing.Annotated[GenerateLessonPlanRequest, fastapi.Body()],
) -> GenerateLessonPlanResponse:
    client = config.get_completion_client()
    uow = config.get_unit_of_work()
    lesson_plan = await generate_lesson_plan.generate_lesson_plan(
        requirements=request.requirements, client=client, uow=uow
    )
    return GenerateLessonPlanResponse(lesson_plan=lesson_plan)


@router.get("/")
async def get_lesson_plans() -> list[lesson_plans.LessonPlan]:
    uow = config.get_unit_of_work()
    return uow.lesson_plans.get_lesson_plans()


@router.get("/{lesson_plan_id}")
async def get_lesson_plan(lesson_plan_id: int) -> lesson_plans.LessonPlan:
    uow = config.get_unit_of_work()
    try:
        return uow.lesson_plans.get_lesson_plan(lesson_plan_id)
    except lesson_plans.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


@router.delete("/{lesson_plan_id}", status_code=204)
async def delete_lesson_plan(lesson_plan_id: int) -> None:
    uow = config.get_unit_of_work()
    try:
        uow.lesson_plans.delete_lesson_plan(lesson_plan_id)
    except lesson_plans.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


class AddSetToSequenceRequest(pydantic.BaseModel):
    exercise_id: int
    reps: int
    duration_seconds: int
    movement_variant: lesson_plans.MovementVariant
    equipment_variant: list[lesson_plans.Equipment]


class AddSetToSequenceResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseSetRequest(pydantic.BaseModel):
    reps: int
    duration_seconds: int
    movement_variant: lesson_plans.MovementVariant
    equipment_variant: list[lesson_plans.Equipment]


@router.post("/sequences/{sequence_id}/sets", status_code=201)
async def add_set_to_sequence(
    sequence_id: int,
    request: typing.Annotated[AddSetToSequenceRequest, fastapi.Body()],
) -> AddSetToSequenceResponse:
    uow = config.get_unit_of_work()
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
        raise fastapi.HTTPException(status_code=404, detail="Sequence not found.")
    except lesson_plans.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@router.put("/sequences/{sequence_id}/sets/{set_id}", status_code=204)
async def update_exercise_set(
    sequence_id: int,
    set_id: int,
    request: typing.Annotated[UpdateExerciseSetRequest, fastapi.Body()],
) -> None:
    uow = config.get_unit_of_work()
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
    sequence_id: int,
    set_id: int,
) -> None:
    uow = config.get_unit_of_work()
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
) -> AddSequenceToSectionResponse:
    uow = config.get_unit_of_work()
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
) -> None:
    uow = config.get_unit_of_work()
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
async def delete_exercise_sequence(sequence_id: int) -> None:
    uow = config.get_unit_of_work()
    try:
        uow.lesson_plans.delete_exercise_sequence(sequence_id)
    except lesson_plans.SequenceDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Sequence not found.")
