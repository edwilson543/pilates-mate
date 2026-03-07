from pilates.domain.lesson_plans._evaluation._metrics import _structural_quality


class TestVariantOrderingComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = _structural_quality.VariantOrderingComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = _structural_quality.VariantOrderingComplianceMetric(value=80.0)

        assert metric.to_numeric_score() == 80.0


class TestEquipmentConsistencyComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = _structural_quality.EquipmentConsistencyComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = _structural_quality.EquipmentConsistencyComplianceMetric(value=75.0)

        assert metric.to_numeric_score() == 75.0


class TestMuscleGroupFocusComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = _structural_quality.MuscleGroupFocusComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = _structural_quality.MuscleGroupFocusComplianceMetric(value=85.0)

        assert metric.to_numeric_score() == 85.0


class TestStartingPositionConsistencyComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = _structural_quality.StartingPositionConsistencyComplianceMetric(
            value=100.0
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_imperfect(self) -> None:
        metric = _structural_quality.StartingPositionConsistencyComplianceMetric(
            value=90.0
        )

        assert metric.to_numeric_score() == 90.0


class TestSectionBalanceMetricScoring:
    def test_to_numeric_score_when_perfect_correlation(self) -> None:
        metric = _structural_quality.SectionBalanceMetric(
            warm_up_percentage=10.0,
            main_session_percentage=80.0,
            cool_down_percentage=10.0,
            correlation_coefficient=1.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_no_correlation(self) -> None:
        metric = _structural_quality.SectionBalanceMetric(
            warm_up_percentage=33.0,
            main_session_percentage=33.0,
            cool_down_percentage=34.0,
            correlation_coefficient=0.0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_negative_correlation(self) -> None:
        metric = _structural_quality.SectionBalanceMetric(
            warm_up_percentage=80.0,
            main_session_percentage=10.0,
            cool_down_percentage=10.0,
            correlation_coefficient=-1.0,
        )

        assert metric.to_numeric_score() == 0.0


class TestTransitionQualityMetricScoring:
    def test_to_numeric_score_when_no_transitions(self) -> None:
        metric = _structural_quality.TransitionQualityMetric(
            total_transitions=10,
            position_changes=0,
            transition_rate=0.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_half_transitions(self) -> None:
        metric = _structural_quality.TransitionQualityMetric(
            total_transitions=10,
            position_changes=5,
            transition_rate=50.0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_all_transitions(self) -> None:
        metric = _structural_quality.TransitionQualityMetric(
            total_transitions=10,
            position_changes=10,
            transition_rate=100.0,
        )

        assert metric.to_numeric_score() == 0.0


class TestProgressiveDifficultyMetricScoring:
    def test_to_numeric_score_when_progressive_with_no_regressions(self) -> None:
        metric = _structural_quality.ProgressiveDifficultyMetric(
            difficulty_trajectory=[1.0, 2.0, 3.0, 4.0],
            is_progressive=True,
            regression_count=0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_progressive_with_some_regressions(self) -> None:
        metric = _structural_quality.ProgressiveDifficultyMetric(
            difficulty_trajectory=[1.0, 3.0, 2.0, 4.0],
            is_progressive=True,
            regression_count=1,
        )

        assert metric.to_numeric_score() == 95.0

    def test_to_numeric_score_when_not_progressive_with_no_regressions(self) -> None:
        metric = _structural_quality.ProgressiveDifficultyMetric(
            difficulty_trajectory=[2.0, 2.0, 2.0, 2.0],
            is_progressive=False,
            regression_count=0,
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_not_progressive_with_many_regressions(self) -> None:
        metric = _structural_quality.ProgressiveDifficultyMetric(
            difficulty_trajectory=[4.0, 3.0, 2.0, 1.0],
            is_progressive=False,
            regression_count=3,
        )

        assert metric.to_numeric_score() == 35.0

    def test_to_numeric_score_when_very_poor(self) -> None:
        metric = _structural_quality.ProgressiveDifficultyMetric(
            difficulty_trajectory=[5.0, 1.0, 1.0, 1.0],
            is_progressive=False,
            regression_count=10,
        )

        assert metric.to_numeric_score() == 0.0
