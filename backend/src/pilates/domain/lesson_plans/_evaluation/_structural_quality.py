from __future__ import annotations

import attrs

from pilates.domain import exercises

from .. import _generation
from . import _base, _requirements_compliance


@attrs.frozen
class SectionBalanceMetric(_base.Metric):
    warm_up_percentage: float
    main_session_percentage: float
    cool_down_percentage: float
    correlation_coefficient: float

    def render(self) -> str:
        return (
            f"Correlation: {self.correlation_coefficient:.2f} "
            f"(warm-up: {self.warm_up_percentage:.1f}%, "
            f"main: {self.main_session_percentage:.1f}%, "
            f"cool-down: {self.cool_down_percentage:.1f}%)"
        )

    @classmethod
    def aggregate(cls, metrics: list[SectionBalanceMetric]) -> SectionBalanceMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        mean_warm_up = sum(m.warm_up_percentage for m in metrics) / len(metrics)
        mean_main_session = sum(m.main_session_percentage for m in metrics) / len(
            metrics
        )
        mean_cool_down = sum(m.cool_down_percentage for m in metrics) / len(metrics)
        mean_correlation = sum(m.correlation_coefficient for m in metrics) / len(
            metrics
        )

        return cls(
            warm_up_percentage=round(mean_warm_up, 1),
            main_session_percentage=round(mean_main_session, 1),
            cool_down_percentage=round(mean_cool_down, 1),
            correlation_coefficient=round(mean_correlation, 2),
        )


class SectionBalance(_base.Evaluator[SectionBalanceMetric]):
    name = "Section balance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Evaluates time distribution across lesson plan sections.
- Ideal: warm-up 10%, main session 80%, cool-down 10%.
- Correlation coefficient shows alignment (1.0 = perfect).
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> SectionBalanceMetric:
        warm_up_duration = sum(
            set.duration_seconds * sequence.reps
            for sequence in generated_plan.warm_up
            for set in sequence.sets
        )
        main_session_duration = sum(
            set.duration_seconds * sequence.reps
            for sequence in generated_plan.main_session
            for set in sequence.sets
        )
        cool_down_duration = sum(
            set.duration_seconds * sequence.reps
            for sequence in generated_plan.cool_down
            for set in sequence.sets
        )

        total_duration = warm_up_duration + main_session_duration + cool_down_duration

        if total_duration == 0:
            warm_up_pct = main_session_pct = cool_down_pct = 0.0
        else:
            warm_up_pct = 100 * warm_up_duration / total_duration
            main_session_pct = 100 * main_session_duration / total_duration
            cool_down_pct = 100 * cool_down_duration / total_duration

        actual = [warm_up_pct, main_session_pct, cool_down_pct]
        ideal = [10.0, 80.0, 10.0]
        correlation = _base.correlation_coefficient(actual, ideal)

        return SectionBalanceMetric(
            warm_up_percentage=warm_up_pct,
            main_session_percentage=main_session_pct,
            cool_down_percentage=cool_down_pct,
            correlation_coefficient=correlation,
        )


@attrs.frozen
class TransitionQualityMetric(_base.Metric):
    total_transitions: int
    position_changes: int
    transition_rate: float

    def render(self) -> str:
        return f"{self.transition_rate}% ({self.position_changes}/{self.total_transitions} transitions require position change)"

    @classmethod
    def aggregate(
        cls, metrics: list[TransitionQualityMetric]
    ) -> TransitionQualityMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

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
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> TransitionQualityMetric:
        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)

        all_sequences = generated_plan.sequences
        total_transitions = len(all_sequences) - 1
        position_changes = 0

        for i in range(total_transitions):
            current_sequence = all_sequences[i]
            next_sequence = all_sequences[i + 1]

            # Get the starting position from the first set in each sequence.
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
    def aggregate(
        cls, metrics: list[ProgressiveDifficultyMetric]
    ) -> ProgressiveDifficultyMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        # Calculate mean trajectory across all metrics.
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
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> ProgressiveDifficultyMetric:
        difficulty_scores = {
            exercises.Difficulty.BEGINNER: 1,
            exercises.Difficulty.INTERMEDIATE: 5,
            exercises.Difficulty.ADVANCED: 10,
        }

        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)

        difficulty_trajectory = []
        for sequence in generated_plan.main_session:
            total_weighted_difficulty = 0.0
            total_duration = 0.0

            for set_item in sequence.sets:
                exercise = exercise_lookup.get(set_item.exercise.id)
                if exercise is None:
                    continue

                difficulty_score = difficulty_scores[exercise.difficulty]
                total_weighted_difficulty += (
                    difficulty_score * set_item.duration_seconds
                )
                total_duration += set_item.duration_seconds

            if total_duration == 0:
                avg_difficulty = 0.0
            else:
                avg_difficulty = total_weighted_difficulty / total_duration

            difficulty_trajectory.append(avg_difficulty)

        # Check if trajectory is generally progressive.
        regression_count = 0
        for i in range(1, len(difficulty_trajectory)):
            if (
                difficulty_trajectory[i]
                < difficulty_trajectory[i - 1] - self.regression_threshold
            ):
                regression_count += 1

        # Consider progressive if there are fewer regressions than progressions.
        is_progressive = regression_count < len(difficulty_trajectory) / 2

        return ProgressiveDifficultyMetric(
            difficulty_trajectory=[round(score, 2) for score in difficulty_trajectory],
            is_progressive=is_progressive,
            regression_count=regression_count,
        )


class VariantOrderingCompliance(
    _base.Evaluator[_requirements_compliance.PercentageMetric]
):
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
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> _requirements_compliance.PercentageMetric:
        compliant_count = 0
        total_sequences = 0

        for sequence in generated_plan.sequences:
            if not sequence.sets:
                continue

            total_sequences += 1
            is_compliant = True

            # Check first set uses STANDARD.
            if sequence.sets[0].movement_variant != exercises.MovementVariant.STANDARD:
                is_compliant = False

            # Check PULSE/HOLD only at end.
            for i, set_item in enumerate(sequence.sets[:-1]):
                if set_item.movement_variant in (
                    exercises.MovementVariant.PULSE,
                    exercises.MovementVariant.HOLD,
                ):
                    is_compliant = False
                    break

            if is_compliant:
                compliant_count += 1

        if total_sequences == 0:
            percentage = 100.0
        else:
            percentage = round(100 * compliant_count / total_sequences, 1)

        return _requirements_compliance.PercentageMetric(value=percentage)


class EquipmentConsistencyCompliance(
    _base.Evaluator[_requirements_compliance.PercentageMetric]
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
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> _requirements_compliance.PercentageMetric:
        compliant_count = 0
        total_sequences = 0

        for sequence in generated_plan.sequences:
            if not sequence.sets:
                continue

            total_sequences += 1

            # Get equipment from first set.
            first_equipment = set(sequence.sets[0].equipment_variant)

            # Check all sets use same equipment.
            is_consistent = all(
                set(set_item.equipment_variant) == first_equipment
                for set_item in sequence.sets
            )

            if is_consistent:
                compliant_count += 1

        if total_sequences == 0:
            percentage = 100.0
        else:
            percentage = round(100 * compliant_count / total_sequences, 1)

        return _requirements_compliance.PercentageMetric(value=percentage)


class MuscleGroupFocusCompliance(
    _base.Evaluator[_requirements_compliance.PercentageMetric]
):
    name = "Muscle group focus compliance"
    category = _base.EvaluationCategory.STRUCTURAL_QUALITY
    description = """Checks that muscle group focus is consistent within each sequence.
- All sets in a sequence should target the same primary muscle group.
- Returns percentage of sequences with consistent muscle group focus.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> _requirements_compliance.PercentageMetric:
        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)

        compliant_count = 0
        total_sequences = 0

        for sequence in generated_plan.sequences:
            if not sequence.sets:
                continue

            total_sequences += 1

            # Get muscle group from first set.
            first_exercise = exercise_lookup.get(sequence.sets[0].exercise.id)
            if first_exercise is None:
                continue

            first_muscle_group = first_exercise.primary_muscle_group

            # Check all sets target same muscle group.
            is_consistent = True
            for set_item in sequence.sets:
                exercise = exercise_lookup.get(set_item.exercise.id)
                if exercise is None:
                    is_consistent = False
                    break
                if exercise.primary_muscle_group != first_muscle_group:
                    is_consistent = False
                    break

            if is_consistent:
                compliant_count += 1

        if total_sequences == 0:
            percentage = 100.0
        else:
            percentage = round(100 * compliant_count / total_sequences, 1)

        return _requirements_compliance.PercentageMetric(value=percentage)


class StartingPositionConsistencyCompliance(
    _base.Evaluator[_requirements_compliance.PercentageMetric]
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
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> _requirements_compliance.PercentageMetric:
        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)

        compliant_count = 0
        total_sequences = 0

        for sequence in generated_plan.sequences:
            if not sequence.sets:
                continue

            total_sequences += 1

            # Get starting position from first set.
            first_exercise = exercise_lookup.get(sequence.sets[0].exercise.id)
            if first_exercise is None:
                continue

            first_position = first_exercise.starting_position

            # Check all sets use same starting position.
            is_consistent = True
            for set_item in sequence.sets:
                exercise = exercise_lookup.get(set_item.exercise.id)
                if exercise is None:
                    is_consistent = False
                    break
                if exercise.starting_position != first_position:
                    is_consistent = False
                    break

            if is_consistent:
                compliant_count += 1

        if total_sequences == 0:
            percentage = 100.0
        else:
            percentage = round(100 * compliant_count / total_sequences, 1)

        return _requirements_compliance.PercentageMetric(value=percentage)
