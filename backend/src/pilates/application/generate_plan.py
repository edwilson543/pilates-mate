import pydantic

from pilates.domain import lesson_planning, templates, vendors

from . import _examples


class _GeneratedLessonPlan(pydantic.BaseModel):
    name: str
    description: str
    warm_up: list[lesson_planning.ExerciseSequence]
    main_session: list[lesson_planning.ExerciseSequence]
    cool_down: list[lesson_planning.ExerciseSequence]


async def generate_lesson_plan(
    *,
    user_prompt: str,
    client: vendors.CompletionClient,
    repository: lesson_planning.Repository,
) -> lesson_planning.LessonPlan:
    exercises = repository.get_exercises()
    example_lesson_plans = _examples.get_text_example_lesson_plans()

    system_prompt = templates.render_system_prompt(
        exercises=exercises, example_lesson_plans=example_lesson_plans
    )

    lesson_plan = await client.get_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_format=_GeneratedLessonPlan,
    )

    lesson_plan_id = repository.create_lesson_plan(
        name=lesson_plan.name,
        description=lesson_plan.description,
        warm_up=lesson_plan.warm_up,
        main_session=lesson_plan.main_session,
        cool_down=lesson_plan.cool_down,
    )

    data = {"id": lesson_plan_id, **lesson_plan.model_dump()}
    return lesson_planning.LessonPlan.model_validate(data)
