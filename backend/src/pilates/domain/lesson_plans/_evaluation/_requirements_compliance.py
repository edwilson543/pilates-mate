from __future__ import annotations

import attrs

from pilates.domain import exercises

from .. import _generation
from . import _base


@attrs.frozen
class PercentageMetric(_base.Metric):
    """Metric for simple percentage values."""

    value: float

    def render(self) -> str:
        return f"{self.value}%"


class DurationCompliance(_base.Evaluator[PercentageMetric]):
    name = "Target duration"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Comparison of the duration of the generated lesson plan relative to the required duration.
- If this is 100%, then the generated lesson plan is the ideal duration.
- If this is less than 100%, then the generated lesson plan is too short.
- If this is greater than 100%, then the generated lesson plan is too long.
A duration in the range 90-110% is deemed acceptable.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> PercentageMetric:
        ratio = generated_plan.duration_minutes / requirements.duration_minutes
        return PercentageMetric(value=round(100 * ratio, 3))


@attrs.frozen
class DifficultyScoreMetric(_base.Metric):
    generated_score: float
    target_score: float
    percentage_of_target: float

    def render(self) -> str:
        return f"{self.percentage_of_target}% (generated: {self.generated_score:.2f}, target: {self.target_score:.2f})"


class DifficultyScore(_base.Evaluator[DifficultyScoreMetric]):
    name = "Difficulty score"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Compares the difficulty distribution of the generated plan against target difficulty.
- Uses scoring: Beginner=1, Intermediate=5, Advanced=10.
- 100% means perfect match, <100% means easier, >100% means harder.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> DifficultyScoreMetric:
        difficulty_scores = {
            exercises.Difficulty.BEGINNER: 1,
            exercises.Difficulty.INTERMEDIATE: 5,
            exercises.Difficulty.ADVANCED: 10,
        }

        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)

        total_weighted_difficulty = 0.0
        total_duration = 0.0

        for set_item in generated_plan.sets:
            exercise = exercise_lookup.get(set_item.exercise.id)
            if exercise is None:
                continue

            weighted_duration = set_item.duration_seconds
            for sequence in generated_plan.sequences:
                if set_item in sequence.sets:
                    weighted_duration *= sequence.reps
                    break

            difficulty_score = difficulty_scores[exercise.difficulty]
            total_weighted_difficulty += difficulty_score * weighted_duration
            total_duration += weighted_duration

        if total_duration == 0:
            generated_score = 0.0
        else:
            generated_score = total_weighted_difficulty / total_duration

        target_score = float(difficulty_scores[requirements.target_difficulty])

        if target_score == 0:
            percentage = 100.0
        else:
            percentage = round(100 * generated_score / target_score, 1)

        return DifficultyScoreMetric(
            generated_score=generated_score,
            target_score=target_score,
            percentage_of_target=percentage,
        )


@attrs.frozen
class MuscleGroupCoverageMetric(_base.Metric):
    percentage_targeting_required_groups: float
    required_groups: list[exercises.MuscleGroup]
    groups_in_plan: list[exercises.MuscleGroup]

    def render(self) -> str:
        return f"{self.percentage_targeting_required_groups}% (required: {self.required_groups}, in plan: {self.groups_in_plan})"


class MuscleGroupCoverage(_base.Evaluator[MuscleGroupCoverageMetric]):
    name = "Muscle group coverage"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of exercise sets whose primary muscle group matches requirements.
- Should be high (e.g., >70%) while allowing complementary exercises.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> MuscleGroupCoverageMetric:
        exercise_lookup = _base.build_exercise_lookup(deps.exercises_repo)
        required_groups_set = set(requirements.target_muscle_groups)

        matching_count = 0
        groups_in_plan_set = set()

        for set_item in generated_plan.sets:
            exercise = exercise_lookup.get(set_item.exercise.id)
            if exercise is None:
                continue

            groups_in_plan_set.add(exercise.primary_muscle_group)
            if exercise.primary_muscle_group in required_groups_set:
                matching_count += 1

        total_count = len(generated_plan.sets)
        if total_count == 0:
            percentage = 0.0
        else:
            percentage = round(100 * matching_count / total_count, 1)

        return MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=percentage,
            required_groups=sorted(requirements.target_muscle_groups),
            groups_in_plan=sorted(groups_in_plan_set),
        )


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


class SectionBalance(_base.Evaluator[SectionBalanceMetric]):
    name = "Section balance"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
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
class EquipmentUtilizationMetric(_base.Metric):
    percentage_utilized: float
    available_equipment: list[exercises.Equipment]
    used_equipment: list[exercises.Equipment]

    def render(self) -> str:
        return f"{self.percentage_utilized}% (available: {self.available_equipment}, used: {self.used_equipment})"


class EquipmentUtilization(_base.Evaluator[EquipmentUtilizationMetric]):
    name = "Equipment utilization"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of available equipment actually used in the plan.
- Higher is better for equipment variety, but 100% is not required.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> EquipmentUtilizationMetric:
        available_equipment = requirements.available_equipment
        used_equipment_set = set()

        for set_item in generated_plan.sets:
            for equipment in set_item.equipment_variant:
                used_equipment_set.add(equipment)

        if not available_equipment:
            percentage = 100.0
        else:
            used_count = len(
                [eq for eq in available_equipment if eq in used_equipment_set]
            )
            percentage = round(100 * used_count / len(available_equipment), 1)

        return EquipmentUtilizationMetric(
            percentage_utilized=percentage,
            available_equipment=sorted(available_equipment),
            used_equipment=sorted(used_equipment_set),
        )
