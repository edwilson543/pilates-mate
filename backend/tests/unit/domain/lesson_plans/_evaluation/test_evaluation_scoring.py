from pilates.domain import lesson_plans
from testing.helpers import lesson_plans as lesson_plan_helpers


class TestGeneratedLessonPlanEvaluationScoring:
    def test_to_numeric_score_when_all_perfect(self) -> None:
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DurationComplianceMetric(value=100.0),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 100.0

    def test_to_numeric_score_when_validation_fails(self) -> None:
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=95.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DurationComplianceMetric(value=100.0),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 25.0

    def test_to_numeric_score_when_validation_passes_but_others_fail(self) -> None:
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.EquipmentValidityMetric(
                        percentage_of_valid_equipment=100.0,
                        invalid_equipment=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DurationComplianceMetric(value=80.0),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.TransitionQualityMetric(
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
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DurationComplianceMetric(value=100.0),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DifficultyScoreMetric(
                        generated_score=5.0,
                        target_score=5.0,
                        percentage_of_target=100.0,
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=5,
                        transition_rate=50.0,
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.ProgressiveDifficultyMetric(
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
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.EquipmentValidityMetric(
                        percentage_of_valid_equipment=100.0,
                        invalid_equipment=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.MovementVariantValidityMetric(
                        percentage_of_valid_variants=100.0,
                        invalid_sets=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.EquipmentVariantValidityMetric(
                        percentage_of_valid_equipment_variants=100.0,
                        invalid_sets=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE,
                    outcome=lesson_plans.DurationComplianceMetric(value=100.0),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY,
                    outcome=lesson_plans.TransitionQualityMetric(
                        total_transitions=10,
                        position_changes=0,
                        transition_rate=0.0,
                    ),
                ),
            ]
        )

        assert evaluation.to_numeric_score() == 100.0

    def test_to_numeric_score_when_one_validation_metric_fails(self) -> None:
        evaluation = lesson_plans.GeneratedLessonPlanEvaluation(
            evaluations=[
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.ExerciseValidityMetric(
                        percentage_of_valid_exercises=100.0,
                        invalid_exercises=[],
                    ),
                ),
                lesson_plan_helpers.Evaluation.build(
                    category=lesson_plans.EvaluationCategory.VALIDATION,
                    outcome=lesson_plans.EquipmentValidityMetric(
                        percentage_of_valid_equipment=90.0,
                        invalid_equipment=[],
                    ),
                ),
            ]
        )

        expected_validation_avg = (100.0 + 0.0) / 2
        expected_score = expected_validation_avg * 0.5

        assert evaluation.to_numeric_score() == expected_score
