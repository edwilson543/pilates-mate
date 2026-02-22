import typing

import fastapi
import pydantic

from pilates import config
from pilates.application import generate_plan
from pilates.domain import lesson_planning


exercise_router = fastapi.APIRouter()
lesson_plan_router = fastapi.APIRouter()


class CreateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: lesson_planning.ExerciseCategory
    difficulty: lesson_planning.Difficulty
    primary_muscle_group: lesson_planning.MuscleGroup
    starting_position: lesson_planning.StartingPosition
    variants: list[lesson_planning.ExerciseVariant]


class CreateExerciseResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseRequest(pydantic.BaseModel):
    name: str
    description: str
    category: lesson_planning.ExerciseCategory
    difficulty: lesson_planning.Difficulty
    primary_muscle_group: lesson_planning.MuscleGroup
    starting_position: lesson_planning.StartingPosition
    variants: list[lesson_planning.ExerciseVariant]


@exercise_router.post("/", status_code=201)
def create_exercise(
    request: typing.Annotated[CreateExerciseRequest, fastapi.Body()],
) -> CreateExerciseResponse:
    repository = config.get_lesson_planning_repository()
    exercise_id = repository.create_exercise(
        name=request.name,
        description=request.description,
        category=request.category,
        difficulty=request.difficulty,
        primary_muscle_group=request.primary_muscle_group,
        starting_position=request.starting_position,
        variants=request.variants,
    )
    return CreateExerciseResponse(id=exercise_id)


@exercise_router.get("/")
def get_exercises() -> list[lesson_planning.Exercise]:
    repository = config.get_lesson_planning_repository()
    return repository.get_exercises()


@exercise_router.get("/{exercise_id}")
def get_exercise(exercise_id: int) -> lesson_planning.Exercise:
    repository = config.get_lesson_planning_repository()
    try:
        return repository.get_exercise(exercise_id)
    except lesson_planning.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@exercise_router.put("/{exercise_id}", status_code=204)
def update_exercise(
    exercise_id: int,
    request: typing.Annotated[UpdateExerciseRequest, fastapi.Body()],
) -> None:
    repository = config.get_lesson_planning_repository()
    try:
        repository.update_exercise(
            id=exercise_id,
            name=request.name,
            description=request.description,
            category=request.category,
            difficulty=request.difficulty,
            primary_muscle_group=request.primary_muscle_group,
            starting_position=request.starting_position,
            variants=request.variants,
        )
    except lesson_planning.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


class GenerateLessonPlanRequest(pydantic.BaseModel):
    requirements: generate_plan.LessonPlanRequirements


class GenerateLessonPlanResponse(pydantic.BaseModel):
    lesson_plan: lesson_planning.LessonPlan


@lesson_plan_router.post("/", status_code=201)
async def generate_lesson_plan(
    request: typing.Annotated[GenerateLessonPlanRequest, fastapi.Body()],
) -> GenerateLessonPlanResponse:
    client = config.get_completion_client()
    repository = config.get_lesson_planning_repository()
    lesson_plan = await generate_plan.generate_lesson_plan(
        requirements=request.requirements,
        client=client,
        repository=repository,
    )
    return GenerateLessonPlanResponse(lesson_plan=lesson_plan)


@lesson_plan_router.get("/")
def get_lesson_plans() -> list[lesson_planning.LessonPlan]:
    repository = config.get_lesson_planning_repository()
    return repository.get_lesson_plans()


@lesson_plan_router.get("/{lesson_plan_id}")
def get_lesson_plan(lesson_plan_id: int) -> lesson_planning.LessonPlan:
    repository = config.get_lesson_planning_repository()
    try:
        return repository.get_lesson_plan(lesson_plan_id)
    except lesson_planning.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


@lesson_plan_router.delete("/{lesson_plan_id}", status_code=204)
def delete_lesson_plan(lesson_plan_id: int) -> None:
    repository = config.get_lesson_planning_repository()
    try:
        repository.delete_lesson_plan(lesson_plan_id)
    except lesson_planning.LessonPlanDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Lesson plan not found.")


class AddSetToSequenceRequest(pydantic.BaseModel):
    exercise_id: int
    reps: int
    duration_seconds: int
    variant: lesson_planning.ExerciseVariant


class AddSetToSequenceResponse(pydantic.BaseModel):
    id: int


class UpdateExerciseSetRequest(pydantic.BaseModel):
    reps: int
    duration_seconds: int
    variant: lesson_planning.ExerciseVariant


@lesson_plan_router.post("/sequences/{sequence_id}/sets", status_code=201)
def add_set_to_sequence(
    sequence_id: int,
    request: typing.Annotated[AddSetToSequenceRequest, fastapi.Body()],
) -> AddSetToSequenceResponse:
    repository = config.get_lesson_planning_repository()
    try:
        set_id = repository.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=request.exercise_id,
            reps=request.reps,
            duration_seconds=request.duration_seconds,
            variant=request.variant,
        )
        return AddSetToSequenceResponse(id=set_id)
    except lesson_planning.SequenceDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Sequence not found.")
    except lesson_planning.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@lesson_plan_router.put("/sequences/{sequence_id}/sets/{set_id}", status_code=204)
def update_exercise_set(
    sequence_id: int,
    set_id: int,
    request: typing.Annotated[UpdateExerciseSetRequest, fastapi.Body()],
) -> None:
    repository = config.get_lesson_planning_repository()
    try:
        repository.update_exercise_set(
            id=set_id,
            reps=request.reps,
            duration_seconds=request.duration_seconds,
            variant=request.variant,
        )
    except lesson_planning.SetDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Set not found.")


@lesson_plan_router.delete("/sequences/{sequence_id}/sets/{set_id}", status_code=204)
def delete_exercise_set(
    sequence_id: int,
    set_id: int,
) -> None:
    repository = config.get_lesson_planning_repository()
    try:
        repository.delete_exercise_set(set_id)
    except lesson_planning.SetDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Set not found.")
