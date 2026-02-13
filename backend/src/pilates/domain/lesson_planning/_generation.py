from pilates.domain import templates

from . import _models


def render_system_prompt(
    *,
    all_exercises: list[_models.Exercise],
    example_lesson_plans: list[_models.LessonPlan],
) -> str:
    prompt_variables = {
        "exercises": all_exercises,
        "example_lesson_plans": example_lesson_plans,
    }

    return templates.render(
        directory="lesson-planning",
        filename="system.jinja",
        variables=prompt_variables,
    )
