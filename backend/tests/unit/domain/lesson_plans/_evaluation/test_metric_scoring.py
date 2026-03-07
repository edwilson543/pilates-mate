from pilates.domain import exercises, lesson_plans


class TestExerciseValidityMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.ExerciseValidityMetric(
            percentage_of_valid_exercises=100.0,
            invalid_exercises=[],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_slightly_imperfect(self) -> None:
        metric = lesson_plans.ExerciseValidityMetric(
            percentage_of_valid_exercises=95.0,
            invalid_exercises=[],
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_very_poor(self) -> None:
        metric = lesson_plans.ExerciseValidityMetric(
            percentage_of_valid_exercises=90.0,
            invalid_exercises=[],
        )

        assert metric.to_numeric_score() == 0.0

    def test_to_numeric_score_when_below_threshold(self) -> None:
        metric = lesson_plans.ExerciseValidityMetric(
            percentage_of_valid_exercises=85.0,
            invalid_exercises=[],
        )

        assert metric.to_numeric_score() == 0.0


class TestEquipmentValidityMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.EquipmentValidityMetric(
            percentage_of_valid_equipment=100.0,
            invalid_equipment=[],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.EquipmentValidityMetric(
            percentage_of_valid_equipment=95.0,
            invalid_equipment=[exercises.Equipment.BALL],
        )

        assert metric.to_numeric_score() == 50.0


class TestMovementVariantValidityMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.MovementVariantValidityMetric(
            percentage_of_valid_variants=100.0,
            invalid_sets=[],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.MovementVariantValidityMetric(
            percentage_of_valid_variants=95.0,
            invalid_sets=[],
        )

        assert metric.to_numeric_score() == 50.0


class TestEquipmentVariantValidityMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.EquipmentVariantValidityMetric(
            percentage_of_valid_equipment_variants=100.0,
            invalid_sets=[],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.EquipmentVariantValidityMetric(
            percentage_of_valid_equipment_variants=92.0,
            invalid_sets=[],
        )

        assert metric.to_numeric_score() == 20.0


class TestDurationComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_within_ideal_range_lower(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=95.0)

        assert metric.to_numeric_score() == 75.0

    def test_to_numeric_score_when_within_ideal_range_upper(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=105.0)

        assert metric.to_numeric_score() == 75.0

    def test_to_numeric_score_when_at_acceptable_boundary(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=90.0)

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_outside_acceptable_range(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=80.0)

        assert metric.to_numeric_score() == 30.0

    def test_to_numeric_score_when_very_poor(self) -> None:
        metric = lesson_plans.DurationComplianceMetric(value=60.0)

        assert metric.to_numeric_score() == 0.0


class TestDifficultyScoreMetricScoring:
    def test_to_numeric_score_when_perfect_match(self) -> None:
        metric = lesson_plans.DifficultyScoreMetric(
            generated_score=5.0,
            target_score=5.0,
            percentage_of_target=100.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_slightly_off(self) -> None:
        metric = lesson_plans.DifficultyScoreMetric(
            generated_score=4.5,
            target_score=5.0,
            percentage_of_target=90.0,
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_very_different(self) -> None:
        metric = lesson_plans.DifficultyScoreMetric(
            generated_score=2.0,
            target_score=5.0,
            percentage_of_target=40.0,
        )

        score = metric.to_numeric_score()
        assert score == 40.0


class TestMuscleGroupCoverageMetricScoring:
    def test_to_numeric_score_when_at_ideal_center(self) -> None:
        metric = lesson_plans.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=80.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_at_ideal_lower_bound(self) -> None:
        metric = lesson_plans.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=70.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_at_ideal_upper_bound(self) -> None:
        metric = lesson_plans.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=90.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_below_ideal_range(self) -> None:
        metric = lesson_plans.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=60.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_above_ideal_range(self) -> None:
        metric = lesson_plans.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=100.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 50.0


class TestEquipmentUtilizationMetricScoring:
    def test_to_numeric_score_when_fully_utilized(self) -> None:
        metric = lesson_plans.EquipmentUtilizationMetric(
            percentage_utilized=100.0,
            available_equipment=[exercises.Equipment.BALL],
            used_equipment=[exercises.Equipment.BALL],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_partially_utilized(self) -> None:
        metric = lesson_plans.EquipmentUtilizationMetric(
            percentage_utilized=50.0,
            available_equipment=[exercises.Equipment.BALL],
            used_equipment=[],
        )

        assert metric.to_numeric_score() == 50.0


class TestVariantOrderingComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.VariantOrderingComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.VariantOrderingComplianceMetric(value=80.0)

        assert metric.to_numeric_score() == 80.0


class TestEquipmentConsistencyComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.EquipmentConsistencyComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.EquipmentConsistencyComplianceMetric(value=75.0)

        assert metric.to_numeric_score() == 75.0


class TestMuscleGroupFocusComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.MuscleGroupFocusComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.MuscleGroupFocusComplianceMetric(value=85.0)

        assert metric.to_numeric_score() == 85.0


class TestStartingPositionConsistencyComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = lesson_plans.StartingPositionConsistencyComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = lesson_plans.StartingPositionConsistencyComplianceMetric(value=90.0)

        assert metric.to_numeric_score() == 90.0


class TestSectionBalanceMetricScoring:
    def test_to_numeric_score_when_perfect_correlation(self) -> None:
        metric = lesson_plans.SectionBalanceMetric(
            warm_up_percentage=10.0,
            main_session_percentage=80.0,
            cool_down_percentage=10.0,
            correlation_coefficient=1.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_no_correlation(self) -> None:
        metric = lesson_plans.SectionBalanceMetric(
            warm_up_percentage=33.0,
            main_session_percentage=33.0,
            cool_down_percentage=34.0,
            correlation_coefficient=0.0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_negative_correlation(self) -> None:
        metric = lesson_plans.SectionBalanceMetric(
            warm_up_percentage=80.0,
            main_session_percentage=10.0,
            cool_down_percentage=10.0,
            correlation_coefficient=-1.0,
        )

        assert metric.to_numeric_score() == 0.0


class TestTransitionQualityMetricScoring:
    def test_to_numeric_score_when_no_transitions(self) -> None:
        metric = lesson_plans.TransitionQualityMetric(
            total_transitions=10,
            position_changes=0,
            transition_rate=0.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_half_transitions(self) -> None:
        metric = lesson_plans.TransitionQualityMetric(
            total_transitions=10,
            position_changes=5,
            transition_rate=50.0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_all_transitions(self) -> None:
        metric = lesson_plans.TransitionQualityMetric(
            total_transitions=10,
            position_changes=10,
            transition_rate=100.0,
        )

        assert metric.to_numeric_score() == 0.0


class TestProgressiveDifficultyMetricScoring:
    def test_to_numeric_score_when_progressive_with_no_regressions(self) -> None:
        metric = lesson_plans.ProgressiveDifficultyMetric(
            difficulty_trajectory=[1.0, 2.0, 3.0, 4.0],
            is_progressive=True,
            regression_count=0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_progressive_with_some_regressions(self) -> None:
        metric = lesson_plans.ProgressiveDifficultyMetric(
            difficulty_trajectory=[1.0, 3.0, 2.0, 4.0],
            is_progressive=True,
            regression_count=1,
        )

        assert metric.to_numeric_score() == 95.0

    def test_to_numeric_score_when_not_progressive_with_no_regressions(self) -> None:
        metric = lesson_plans.ProgressiveDifficultyMetric(
            difficulty_trajectory=[2.0, 2.0, 2.0, 2.0],
            is_progressive=False,
            regression_count=0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_not_progressive_with_many_regressions(self) -> None:
        metric = lesson_plans.ProgressiveDifficultyMetric(
            difficulty_trajectory=[4.0, 3.0, 2.0, 1.0],
            is_progressive=False,
            regression_count=3,
        )

        assert metric.to_numeric_score() == 35.0

    def test_to_numeric_score_when_very_poor(self) -> None:
        metric = lesson_plans.ProgressiveDifficultyMetric(
            difficulty_trajectory=[5.0, 1.0, 1.0, 1.0],
            is_progressive=False,
            regression_count=10,
        )

        assert metric.to_numeric_score() == 0.0
