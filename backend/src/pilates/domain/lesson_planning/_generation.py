from pilates.domain import templates

from . import _repository


def render_system_prompt(
    *,
    repository: _repository.Repository,
) -> str:
    exercises = repository.get_exercises()
    lesson_plans = repository.get_lesson_plans()

    prompt_variables = {
        "exercises": exercises,
        "example_lesson_plans": lesson_plans,
    }

    return templates.render(
        directory="lesson-planning",
        filename="system.jinja",
        variables=prompt_variables,
    )
