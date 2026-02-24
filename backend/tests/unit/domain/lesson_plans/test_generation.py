from pilates.domain.lesson_plans import _generation, _models
from testing.helpers import lesson_plans as lesson_plan_helpers


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        lesson_plan = lesson_plan_helpers.LessonPlan()
        exercise = lesson_plan_helpers.Exercise()

        system_prompt = _generation.render_system_prompt(
            duration_minutes=30,
            target_difficulty=_models.Difficulty.INTERMEDIATE,
            target_muscle_groups=[_models.MuscleGroup.GLUTES],
            available_equipment=[_models.Equipment.BALL],
            all_exercises=[exercise],
            example_lesson_plans=[lesson_plan],
        )

        assert system_prompt is not None
