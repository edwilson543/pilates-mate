import typing

import fastapi
import pydantic

from pilates import config
from pilates.domain import lesson_planning


router = fastapi.APIRouter()


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


@router.post("/", status_code=201)
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


@router.get("/")
def get_exercises() -> list[lesson_planning.Exercise]:
    repository = config.get_lesson_planning_repository()
    return repository.get_exercises()


@router.get("/{exercise_id}")
def get_exercise(exercise_id: int) -> lesson_planning.Exercise:
    repository = config.get_lesson_planning_repository()
    try:
        return repository.get_exercise(exercise_id)
    except lesson_planning.ExerciseDoesNotExist:
        raise fastapi.HTTPException(status_code=404, detail="Exercise not found.")


@router.put("/{exercise_id}", status_code=204)
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
