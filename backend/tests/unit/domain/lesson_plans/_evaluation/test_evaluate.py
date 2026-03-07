import pytest

from pilates.domain.lesson_plans import _evaluation
from pilates.domain.lesson_plans._evaluation import _metrics
from pilates.domain.lesson_plans._evaluation._metrics import (
    _requirements_compliance,
    _structural_quality,
    _validity,
)
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


class TestGeneratedLessonPlanEvaluationScoring:
    def test_to_numeric_score_when_all_perfect(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DurationComplianceMetric(
                        value=100.0
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 100.0

    def test_to_numeric_score_when_validation_fails(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=95.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DurationComplianceMetric(
                        value=100.0
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 25.0

    def test_to_numeric_score_when_validation_passes_but_others_fail(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.EquipmentValidityMetric(
                        percentage_of_valid_equipment=100.0,
                        invalid_equipment=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DurationComplianceMetric(
                        value=80.0
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=10,
                        transition_rate=100.0,
                    ),
                ),
            ]
        )

        score = evaluation.to_numeric_score()
        assert 30.0 < score < 50.0

    def test_to_numeric_score_with_weighted_categories(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DurationComplianceMetric(
                        value=100.0
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DifficultyScoreMetric(
                        generated_score=5.0,
                        target_score=5.0,
                        percentage_of_target=100.0,
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=5,
                        transition_rate=50.0,
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.ProgressiveDifficultyMetric(
                        difficulty_trajectory=[1.0, 2.0, 3.0],
                        is_progressive=True,
                        regression_count=0,
                    ),
                ),
            ]
        )

        score = evaluation.to_numeric_score()
        expected_validation_avg = 100.0
        expected_requirements_avg = 100.0
        expected_structural_avg = (50.0 + 100.0) / 2
        expected = (
            (expected_validation_avg * 0.4)
            + (expected_requirements_avg * 0.3)
            + (expected_structural_avg * 0.3)
        )
        assert abs(score - expected) < 0.1

    def test_to_numeric_score_with_multiple_validation_metrics(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.EquipmentValidityMetric(
                        percentage_of_valid_equipment=100.0,
                        invalid_equipment=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.MovementVariantValidityMetric(
                        percentage_of_valid_variants=100.0,
                        invalid_sets=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.EquipmentVariantValidityMetric(
                        percentage_of_valid_equipment_variants=100.0,
                        invalid_sets=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=_requirements_compliance.DurationComplianceMetric(
                        value=100.0
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=_structural_quality.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 100.0

    def test_to_numeric_score_when_one_validation_metric_fails(self) -> None:
        evaluation = _evaluation.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=_metrics.EvaluationCategory.VALIDATION,
                    outcome=_validity.EquipmentValidityMetric(
                        percentage_of_valid_equipment=90.0,
                        invalid_equipment=[],
                    ),
                ),
            ]
        )

        expected_validation_avg = (100.0 + 0.0) / 2
        expected_score = expected_validation_avg * 0.5

        assert evaluation.to_numeric_score() == expected_score
