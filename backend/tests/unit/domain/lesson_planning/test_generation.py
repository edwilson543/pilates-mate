from pilates.domain.lesson_planning import _generation
from testing.helpers import lesson_planning as lesson_planning_helpers


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        lesson_plan = lesson_planning_helpers.LessonPlan()
        exercise = lesson_planning_helpers.Exercise()

        system_prompt = _generation.render_system_prompt(
            all_exercises=[exercise],
            example_lesson_plans=[lesson_plan],
        )

        assert system_prompt is not None
