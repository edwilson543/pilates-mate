import typing

import fastapi
import pydantic

from pilates.domain import exercises
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
    equipment_variants: list[exercises.Equipment]


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
    equipment_variants: list[exercises.Equipment]


@router.post("/", status_code=201)
async def create_exercise(
    request: typing.Annotated[CreateExerciseRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> CreateExerciseResponse:
    exercise_id = uow.exercises.create_exercise(
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
async def get_exercises(uow: dependencies.UnitOfWorkT) -> list[schemas.Exercise]:
    all_exercises = uow.exercises.get_exercises()
    return [schemas.Exercise.from_domain(exercise) for exercise in all_exercises]


@router.get("/{exercise_id}")
async def get_exercise(
    exercise_id: int, uow: dependencies.UnitOfWorkT
) -> schemas.Exercise:
    try:
        domain_exercise = uow.exercises.get_exercise(exercise_id)
        return schemas.Exercise.from_domain(obj=domain_exercise)
    except exercises.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@router.put("/{exercise_id}", status_code=204)
async def update_exercise(
    exercise_id: int,
    request: typing.Annotated[UpdateExerciseRequest, fastapi.Body()],
    uow: dependencies.UnitOfWorkT,
) -> None:
    try:
        uow.exercises.update_exercise(
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
    except exercises.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")
