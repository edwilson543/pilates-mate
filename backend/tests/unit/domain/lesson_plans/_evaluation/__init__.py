from pilates.domain import exercises
from pilates.domain.lesson_plans import _evaluation, _models
from testing.helpers import exercises as exercises_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers


def get_evaluation_deps(
    exercises: list[exercises.Exercise] | None = None,
    lesson_plans: list[_models.LessonPlan] | None = None,
) -> _evaluation.EvaluationDeps:
    """Helper to create evaluation dependencies for testing."""
    exercises_repo = exercises_helpers.FakeRepository(exercises=exercises or [])
    lesson_plan_repo = lesson_plan_helpers.FakeRepository(
        lesson_plans=lesson_plans or []
    )
    return _evaluation.EvaluationDeps(
        exercises_repo=exercises_repo, lesson_plan_repo=lesson_plan_repo
    )
