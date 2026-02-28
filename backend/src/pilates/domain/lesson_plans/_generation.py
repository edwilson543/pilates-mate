from pilates.domain import exercises, templates

from . import _models


def render_system_prompt(
    *,
    duration_minutes: int,
    target_difficulty: exercises.Difficulty,
    target_muscle_groups: list[exercises.MuscleGroup],
    available_equipment: list[exercises.Equipment],
    all_exercises: list[exercises.Exercise],
    example_lesson_plans: list[_models.LessonPlan],
) -> str:
    prompt_variables = {
        "duration_minutes": duration_minutes,
        "target_difficulty": target_difficulty,
        "target_muscle_groups": target_muscle_groups,
        "available_equipment": available_equipment,
        "exercises": {exercise.id: exercise for exercise in all_exercises},
        "example_lesson_plans": example_lesson_plans,
    }

    return templates.render(
        directory="lesson-planning",
        filename="system.jinja",
        variables=prompt_variables,
    )
