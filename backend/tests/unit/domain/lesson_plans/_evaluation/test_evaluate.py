import pytest

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


class TestAggregate:
    def test_calculates_mean_of_multiple_evaluations(self):
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan()
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps()

        evaluation_1 = _evaluation.evaluate_generated_lesson_plan(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )
        evaluation_2 = _evaluation.evaluate_generated_lesson_plan(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )
        evaluation_3 = _evaluation.evaluate_generated_lesson_plan(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        result = _evaluation.GeneratedLessonPlanEvaluation.aggregate(
            [evaluation_1, evaluation_2, evaluation_3]
        )

        assert len(result.evaluations) == len(evaluation_1.evaluations)
        summary = result.render()
        assert "# Validation" in summary
        assert "# Requirements compliance" in summary

    def test_raises_error_when_evaluations_list_is_empty(self):
        with pytest.raises(ValueError, match="Cannot calculate mean of empty"):
            _evaluation.GeneratedLessonPlanEvaluation.aggregate([])
