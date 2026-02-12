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


async def generate_lesson_plan(
    *,
    user_prompt: str,
    client: vendors.CompletionClient,
    repository: lesson_planning.Repository,
) -> lesson_planning.LessonPlan:
    system_prompt = _get_system_prompt(repository)

    lesson_plan = await client.get_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
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


def _get_system_prompt(repository: lesson_planning.Repository) -> str:
    all_exercises = repository.get_exercises()

    all_lesson_plans = repository.get_lesson_plans()
    # Use the three most recent lesson plans as examples.
    example_lesson_plans = sorted(all_lesson_plans, key=lambda lp: lp.date)[-3:]

    return lesson_planning.render_system_prompt(
        all_exercises=all_exercises, example_lesson_plans=example_lesson_plans
    )
