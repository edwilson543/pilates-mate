from pilates.domain import templates

from . import _models


def render_system_prompt(
    *,
    duration_minutes: int,
    target_difficulty: _models.Difficulty,
    target_muscle_groups: list[_models.MuscleGroup],
    all_exercises: list[_models.Exercise],
    example_lesson_plans: list[_models.LessonPlan],
) -> str:
    prompt_variables = {
        "duration_minutes": duration_minutes,
        "target_difficulty": target_difficulty,
        "target_muscle_groups": target_muscle_groups,
        "exercises": all_exercises,
        "example_lesson_plans": example_lesson_plans,
    }

    return templates.render(
        directory="lesson-planning",
        filename="system.jinja",
        variables=prompt_variables,
    )
