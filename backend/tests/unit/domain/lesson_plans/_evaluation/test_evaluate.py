from pilates.domain.lesson_plans import _evaluation
from testing.helpers import lesson_plans as lesson_plan_helpers

from . import get_evaluation_deps


class TestEvaluateGeneratedLessonPlan:
    def test_smoke_test(self):
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan()
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps()

        result = _evaluation.evaluate_generated_lesson_plan(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )
        summary = result.render()

        # Check validation section.
        assert "# Validation" in summary
        assert "## Exercise validity" in summary
        assert "## Equipment validity" in summary
        assert "## Movement variant validity" in summary
        assert "## Equipment variant validity" in summary

        # Check requirements compliance section.
        assert "# Requirements compliance" in summary
        assert "## Target duration" in summary
        assert "## Difficulty score" in summary
        assert "## Muscle group coverage" in summary
        assert "## Section balance" in summary
        assert "## Equipment utilization" in summary
