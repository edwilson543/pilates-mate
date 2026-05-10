from __future__ import annotations

import collections.abc

import attrs

from pilates.domain import exercises
from pilates.domain.lesson_plans import _generation, _models

from . import _base, _helpers, _requirements_compliance


def _percentage_compliant(
    sequences: list[_generation.GeneratedExerciseSequence],
    is_compliant: collections.abc.Callable[
        [_generation.GeneratedExerciseSequence], bool
    ],
) -> float:
    total = 0
    compliant = 0
    for sequence in sequences:
        if not sequence.sets:
            continue
        total += 1
        if is_compliant(sequence):
            compliant += 1
    if total == 0:
        return 100.0
    return round(100 * compliant / total, 1)


@attrs.frozen
class SectionBalanceMetric(_base.Metric):
    warm_up_percentage: float
    main_session_percentage: float
    cool_down_percentage: float
    balance_score: float

    def render(self) -> str:
        return (
            f"Balance score: {self.balance_score} "
            f"(warm-up: {self.warm_up_percentage}%, "
            f"main: {self.main_session_percentage}%, "
            f"cool-down: {self.cool_down_percentage}%)"
        )

    @classmethod
    def _aggregate(cls, metrics: list[SectionBalanceMetric]) -> SectionBalanceMetric:
        mean_warm_up = sum(m.warm_up_percentage for m in metrics) / len(metrics)
        mean_main_session = sum(m.main_session_percentage for m in metrics) / len(
            metrics
        )
        mean_cool_down = sum(m.cool_down_percentage for m in metrics) / len(metrics)
        mean_balance_score = sum(m.balance_score for m in metrics) / len(metrics)

        return cls(
            warm_up_percentage=round(mean_warm_up, 1),
            main_session_percentage=round(mean_main_session, 1),
            cool_down_percentage=round(mean_cool_down, 1),
            balance_score=round(mean_balance_score, 1),
        )

    def to_numeric_score(self) -> float:
        return self.balance_score


class SectionBalance(_base.Evaluator[SectionBalanceMetric]):
    name = "Section balance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Evaluates time distribution across lesson plan sections.
- Ideal: warm-up 10%, main session 80%, cool-down 10%.
- Balance score shows alignment (100 = perfect, 0 = completely off).
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> SectionBalanceMetric:
        warm_up_duration = generated_plan.warm_up_duration_seconds
        main_session_duration = generated_plan.main_session_duration_seconds
        cool_down_duration = generated_plan.cool_down_duration_seconds

        total_duration = warm_up_duration + main_session_duration + cool_down_duration

        if total_duration == 0:
            warm_up_pct = main_session_pct = cool_down_pct = 0.0
        else:
            warm_up_pct = 100 * warm_up_duration / total_duration
            main_session_pct = 100 * main_session_duration / total_duration
            cool_down_pct = 100 * cool_down_duration / total_duration

        ideal = [10.0, 80.0, 10.0]
        actual = [warm_up_pct, main_session_pct, cool_down_pct]
        total_deviation = sum(abs(a - i) for a, i in zip(actual, ideal))
        balance_score = round(max(0.0, 100.0 - total_deviation), 1)

        return SectionBalanceMetric(
            warm_up_percentage=round(warm_up_pct, 1),
            main_session_percentage=round(main_session_pct, 1),
            cool_down_percentage=round(cool_down_pct, 1),
            balance_score=balance_score,
        )


@attrs.frozen
class TransitionQualityMetric(_base.Metric):
    total_transitions: int
    position_changes: int
    transition_rate: float

    def render(self) -> str:
        return f"{self.transition_rate}% ({self.position_changes}/{self.total_transitions} transitions require position change)"

    @classmethod
    def _aggregate(
        cls, metrics: list[TransitionQualityMetric]
    ) -> TransitionQualityMetric:
        total_transitions_sum = sum(m.total_transitions for m in metrics)
        position_changes_sum = sum(m.position_changes for m in metrics)

        if total_transitions_sum == 0:
            mean_transition_rate = 0.0
        else:
            mean_transition_rate = 100 * position_changes_sum / total_transitions_sum

        return cls(
            total_transitions=total_transitions_sum,
            position_changes=position_changes_sum,
            transition_rate=round(mean_transition_rate, 1),
        )

    def to_numeric_score(self) -> float:
        return max(0.0, 100.0 - self.transition_rate)


class TransitionQuality(_base.Evaluator[TransitionQualityMetric]):
    name = "Transition quality"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Measures smoothness of flow by counting position changes between sequences.
- Lower percentages are better (fewer position changes = smoother flow).
- Position changes are counted between consecutive sequences across all sections.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> TransitionQualityMetric:
        exercise_lookup = deps.build_exercise_lookup()

        all_sequences = generated_plan.sequences
        total_transitions = len(all_sequences) - 1
        position_changes = 0

        for i in range(total_transitions):
            current_sequence = all_sequences[i]
            next_sequence = all_sequences[i + 1]

            if not current_sequence.sets or not next_sequence.sets:
                continue

            current_exercise_id = current_sequence.sets[0].exercise.id
            next_exercise_id = next_sequence.sets[0].exercise.id

            current_exercise = exercise_lookup.get(current_exercise_id)
            next_exercise = exercise_lookup.get(next_exercise_id)

            if current_exercise is None or next_exercise is None:
                continue

            if current_exercise.starting_position != next_exercise.starting_position:
                position_changes += 1

        if total_transitions == 0:
            transition_rate = 0.0
        else:
            transition_rate = round(100 * position_changes / total_transitions, 1)

        return TransitionQualityMetric(
            total_transitions=total_transitions,
            position_changes=position_changes,
            transition_rate=transition_rate,
        )


@attrs.frozen
class ProgressiveDifficultyMetric(_base.Metric):
    difficulty_trajectory: list[float]
    is_progressive: bool
    regression_count: int

    def render(self) -> str:
        trajectory_str = ", ".join(
            f"{score:.2f}" for score in self.difficulty_trajectory
        )
        progressive_status = "Yes" if self.is_progressive else "No"
        return f"Progressive: {progressive_status} (regressions: {self.regression_count}, trajectory: [{trajectory_str}])"

    @classmethod
    def _aggregate(
        cls, metrics: list[ProgressiveDifficultyMetric]
    ) -> ProgressiveDifficultyMetric:
        max_length = max(len(m.difficulty_trajectory) for m in metrics)
        mean_trajectory = []

        for i in range(max_length):
            values_at_position = [
                m.difficulty_trajectory[i]
                for m in metrics
                if i < len(m.difficulty_trajectory)
            ]
            if values_at_position:
                mean_trajectory.append(
                    round(sum(values_at_position) / len(values_at_position), 2)
                )

        mean_is_progressive = sum(m.is_progressive for m in metrics) / len(metrics)
        mean_regression_count = sum(m.regression_count for m in metrics) / len(metrics)

        return cls(
            difficulty_trajectory=mean_trajectory,
            is_progressive=mean_is_progressive > 0.5,
            regression_count=round(mean_regression_count),
        )

    def to_numeric_score(self) -> float:
        return 100.0 if self.is_progressive else 0.0


class ProgressiveDifficulty(_base.Evaluator[ProgressiveDifficultyMetric]):
    name = "Progressive difficulty"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Measures whether difficulty increases through the main session.
- Sequences should get gradually harder during the class.
- Regression count shows how many times difficulty drops significantly.
"""

    regression_threshold: float = 1.5

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> ProgressiveDifficultyMetric:
        exercise_lookup = deps.build_exercise_lookup()

        difficulty_trajectory = []
        for sequence in generated_plan.main_session:
            total_weighted_difficulty = 0.0
            total_duration = 0.0

            for set_item in sequence.sets:
                exercise = exercise_lookup.get(set_item.exercise.id)
                if exercise is None:
                    continue

                total_weighted_difficulty += (
                    _helpers.difficulty_score(exercise.difficulty)
                    * set_item.duration_seconds
                )
                total_duration += set_item.duration_seconds

            if total_duration == 0:
                avg_difficulty = 0.0
            else:
                avg_difficulty = total_weighted_difficulty / total_duration

            difficulty_trajectory.append(avg_difficulty)

        regression_count = sum(
            1
            for i in range(1, len(difficulty_trajectory))
            if difficulty_trajectory[i]
            < difficulty_trajectory[i - 1] - self.regression_threshold
        )
        is_progressive = regression_count < len(difficulty_trajectory) / 2

        return ProgressiveDifficultyMetric(
            difficulty_trajectory=[round(score, 2) for score in difficulty_trajectory],
            is_progressive=is_progressive,
            regression_count=regression_count,
        )


class VariantOrderingComplianceMetric(_requirements_compliance.PercentageMetric): ...


class VariantOrderingCompliance(_base.Evaluator[VariantOrderingComplianceMetric]):
    name = "Variant ordering compliance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Checks that sequences follow proper variant ordering rules.
- First set in a sequence should use STANDARD variant.
- PULSE/HOLD variants should only appear at sequence ends (last set).
- Returns percentage of sequences following these rules.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> VariantOrderingComplianceMetric:
        def is_compliant(
            sequence: _generation.GeneratedExerciseSequence,
        ) -> bool:
            if sequence.sets[0].movement_variant != exercises.MovementVariant.STANDARD:
                return False
            return not any(
                s.movement_variant
                in (exercises.MovementVariant.PULSE, exercises.MovementVariant.HOLD)
                for s in sequence.sets[:-1]
            )

        return VariantOrderingComplianceMetric(
            value=_percentage_compliant(generated_plan.sequences, is_compliant)
        )


class EquipmentConsistencyComplianceMetric(
    _requirements_compliance.PercentageMetric
): ...


class EquipmentConsistencyCompliance(
    _base.Evaluator[EquipmentConsistencyComplianceMetric]
):
    name = "Equipment consistency compliance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Checks that equipment usage is consistent within each sequence.
- All sets in a sequence should use the same equipment (or none).
- Returns percentage of sequences with consistent equipment usage.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> EquipmentConsistencyComplianceMetric:
        def is_compliant(
            sequence: _generation.GeneratedExerciseSequence,
        ) -> bool:
            first_equipment = frozenset(sequence.sets[0].equipment_variant)
            return all(
                frozenset(s.equipment_variant) == first_equipment
                for s in sequence.sets[1:]
            )

        return EquipmentConsistencyComplianceMetric(
            value=_percentage_compliant(generated_plan.sequences, is_compliant)
        )


class MuscleGroupFocusComplianceMetric(_requirements_compliance.PercentageMetric): ...


class MuscleGroupFocusCompliance(_base.Evaluator[MuscleGroupFocusComplianceMetric]):
    name = "Muscle group focus compliance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Checks that muscle group focus is consistent within each sequence.
- All sets in a sequence should target the same primary muscle group.
- Returns percentage of sequences with consistent muscle group focus.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> MuscleGroupFocusComplianceMetric:
        exercise_lookup = deps.build_exercise_lookup()

        def is_compliant(
            sequence: _generation.GeneratedExerciseSequence,
        ) -> bool:
            first_exercise = exercise_lookup.get(sequence.sets[0].exercise.id)
            if first_exercise is None:
                return False
            first_group = first_exercise.primary_muscle_group
            for s in sequence.sets[1:]:
                ex = exercise_lookup.get(s.exercise.id)
                if ex is None or ex.primary_muscle_group != first_group:
                    return False
            return True

        return MuscleGroupFocusComplianceMetric(
            value=_percentage_compliant(generated_plan.sequences, is_compliant)
        )


class StartingPositionConsistencyComplianceMetric(
    _requirements_compliance.PercentageMetric
): ...


class StartingPositionConsistencyCompliance(
    _base.Evaluator[StartingPositionConsistencyComplianceMetric]
):
    name = "Starting position consistency compliance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Checks that starting position is consistent within each sequence.
- All exercises in a sequence should share the same starting position.
- Returns percentage of sequences with consistent starting position.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> StartingPositionConsistencyComplianceMetric:
        exercise_lookup = deps.build_exercise_lookup()

        def is_compliant(
            sequence: _generation.GeneratedExerciseSequence,
        ) -> bool:
            first_exercise = exercise_lookup.get(sequence.sets[0].exercise.id)
            if first_exercise is None:
                return False
            first_position = first_exercise.starting_position
            for s in sequence.sets[1:]:
                ex = exercise_lookup.get(s.exercise.id)
                if ex is None or ex.starting_position != first_position:
                    return False
            return True

        return StartingPositionConsistencyComplianceMetric(
            value=_percentage_compliant(generated_plan.sequences, is_compliant)
        )
