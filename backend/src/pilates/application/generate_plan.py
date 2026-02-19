import datetime as dt

import pydantic

from pilates.domain import lesson_planning, vendors


class _GeneratedLessonPlan(pydantic.BaseModel):
    name: str
    description: str
    date: dt.date
    warm_up: list[lesson_planning.ExerciseSequence]
    main_session: list[lesson_planning.ExerciseSequence]
    cool_down: list[lesson_planning.ExerciseSequence]


class LessonPlanRequirements(pydantic.BaseModel):
    duration_minutes: int
    target_difficulty: lesson_planning.Difficulty
    target_muscle_groups: list[lesson_planning.MuscleGroup]
    user_prompt: str


async def generate_lesson_plan(
    *,
    requirements: LessonPlanRequirements,
    client: vendors.CompletionClient,
    repository: lesson_planning.Repository,
) -> lesson_planning.LessonPlan:
    system_prompt = _get_system_prompt(requirements, repository)

    lesson_plan = await client.get_completion(
        system_prompt=system_prompt,
        user_prompt=requirements.user_prompt,
        output_format=_GeneratedLessonPlan,
    )

    lesson_plan_id = repository.create_lesson_plan(
        name=lesson_plan.name,
        description=lesson_plan.description,
        date=dt.datetime.now().date(),
        warm_up=lesson_plan.warm_up,
        main_session=lesson_plan.main_session,
        cool_down=lesson_plan.cool_down,
    )

    data = {"id": lesson_plan_id, **lesson_plan.model_dump()}
    return lesson_planning.LessonPlan.model_validate(data)


def _get_system_prompt(
    requirements: LessonPlanRequirements,
    repository: lesson_planning.Repository,
) -> str:
    # TODO -> filter exercises by the available equipment.
    all_exercises = repository.get_exercises()

    all_lesson_plans = repository.get_lesson_plans()
    # Use the three most recent lesson plans as examples.
    example_lesson_plans = sorted(all_lesson_plans, key=lambda lp: lp.date)[-3:]

    return lesson_planning.render_system_prompt(
        duration_minutes=requirements.duration_minutes,
        target_difficulty=requirements.target_difficulty,
        target_muscle_groups=requirements.target_muscle_groups,
        all_exercises=all_exercises,
        example_lesson_plans=example_lesson_plans,
    )
