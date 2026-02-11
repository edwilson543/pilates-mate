import typing

import fastapi
import pydantic

from pilates.domain import lesson_planning


exercise_router = fastapi.APIRouter()
lesson_plan_router = fastapi.APIRouter()


class CreateExerciseRequest(pydantic.BaseModel):
    pass


class CreateExerciseResponse(pydantic.BaseModel):
    pass


@exercise_router.post("/")
def create_exercise(
    request: typing.Annotated[
        CreateExerciseRequest, fastapi.Body(CreateExerciseRequest)
    ],
) -> CreateExerciseResponse:
    pass


@exercise_router.get("/")
def get_exercises() -> list[lesson_planning.Exercise]:
    pass


class GenerateLessonPlanRequest(pydantic.BaseModel):
    pass


class GenerateLessonPlanResponse(pydantic.BaseModel):
    pass


@lesson_plan_router.post("/")
def generate_lesson_plan(
    request: typing.Annotated[GenerateLessonPlanRequest, fastapi.Body()],
) -> GenerateLessonPlanResponse:
    pass


@lesson_plan_router.post("/")
def get_lesson_plans() -> list[lesson_planning.LessonPlan]:
    pass
