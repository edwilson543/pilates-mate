import typing

import fastapi
import pydantic

from pilates import config
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
    equipment_variants: list[lesson_plans.Equipment]


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
    equipment_variants: list[lesson_plans.Equipment]


@router.post("/", status_code=201)
def create_exercise(
    request: typing.Annotated[CreateExerciseRequest, fastapi.Body()],
) -> CreateExerciseResponse:
    repository = config.get_lesson_plans_repository()
    exercise_id = repository.create_exercise(
        name=request.name,
        description=request.description,
        category=request.category,
        difficulty=request.difficulty,
        primary_muscle_group=request.primary_muscle_group,
        starting_position=request.starting_position,
        movement_variants=request.movement_variants,
        equipment_variants=request.equipment_variants,
    )
    return CreateExerciseResponse(id=exercise_id)


@router.get("/")
def get_exercises() -> list[lesson_plans.Exercise]:
    repository = config.get_lesson_plans_repository()
    return repository.get_exercises()


@router.get("/{exercise_id}")
def get_exercise(exercise_id: int) -> lesson_plans.Exercise:
    repository = config.get_lesson_plans_repository()
    try:
        return repository.get_exercise(exercise_id)
    except lesson_plans.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@router.put("/{exercise_id}", status_code=204)
def update_exercise(
    exercise_id: int,
    request: typing.Annotated[UpdateExerciseRequest, fastapi.Body()],
) -> None:
    repository = config.get_lesson_plans_repository()
    try:
        repository.update_exercise(
            id=exercise_id,
            name=request.name,
            description=request.description,
            category=request.category,
            difficulty=request.difficulty,
            primary_muscle_group=request.primary_muscle_group,
            starting_position=request.starting_position,
            movement_variants=request.movement_variants,
            equipment_variants=request.equipment_variants,
        )
    except lesson_plans.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")
