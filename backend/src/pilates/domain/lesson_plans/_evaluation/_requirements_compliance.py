from __future__ import annotations

import attrs

from pilates.domain import exercises

from .. import _generation
from . import _base


@attrs.frozen
class PercentageMetric(_base.Metric):
    """Base class for percentage-based metrics. Do not use directly."""

    value: float

    def render(self) -> str:
        return f"{self.value}%"

    @classmethod
    def aggregate(cls, metrics: list[PercentageMetric]) -> PercentageMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        mean_value = sum(m.value for m in metrics) / len(metrics)
        return cls(value=round(mean_value, 3))


@attrs.frozen
class DurationComplianceMetric(PercentageMetric):
    """Duration compliance: 90-110% ideal, 100% perfect."""

    def to_numeric_score(self) -> float:
        distance = abs(self.value - 100.0)
        if distance <= 10.0:
            return 100.0 - (distance * 5.0)
        else:
            return max(0.0, 50.0 - ((distance - 10.0) * 2.0))


@attrs.frozen
class VariantOrderingComplianceMetric(PercentageMetric):
    """Variant ordering compliance: higher is better."""

    def to_numeric_score(self) -> float:
        return self.value


@attrs.frozen
class EquipmentConsistencyComplianceMetric(PercentageMetric):
    """Equipment consistency: higher is better."""

    def to_numeric_score(self) -> float:
        return self.value


@attrs.frozen
class MuscleGroupFocusComplianceMetric(PercentageMetric):
    """Muscle group focus: higher is better."""

    def to_numeric_score(self) -> float:
        return self.value


@attrs.frozen
class StartingPositionConsistencyComplianceMetric(PercentageMetric):
    """Starting position consistency: higher is better."""

    def to_numeric_score(self) -> float:
        return self.value


class DurationCompliance(_base.Evaluator[DurationComplianceMetric]):
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
    ) -> DurationComplianceMetric:
        ratio = generated_plan.duration_minutes / requirements.duration_minutes
        return DurationComplianceMetric(value=round(100 * ratio, 3))


@attrs.frozen
class DifficultyScoreMetric(_base.Metric):
    generated_score: float
    target_score: float
    percentage_of_target: float

    def render(self) -> str:
        return f"{self.percentage_of_target}% (generated: {self.generated_score:.2f}, target: {self.target_score:.2f})"

    @classmethod
    def aggregate(cls, metrics: list[DifficultyScoreMetric]) -> DifficultyScoreMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        mean_generated_score = sum(m.generated_score for m in metrics) / len(metrics)
        mean_target_score = sum(m.target_score for m in metrics) / len(metrics)
        mean_percentage = sum(m.percentage_of_target for m in metrics) / len(metrics)

        return cls(
            generated_score=round(mean_generated_score, 2),
            target_score=round(mean_target_score, 2),
            percentage_of_target=round(mean_percentage, 1),
        )

    def to_numeric_score(self) -> float:
        distance = abs(self.percentage_of_target - 100.0)
        return max(0.0, 100.0 - distance)


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

    @classmethod
    def aggregate(
        cls, metrics: list[MuscleGroupCoverageMetric]
    ) -> MuscleGroupCoverageMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        mean_percentage = sum(
            m.percentage_targeting_required_groups for m in metrics
        ) / len(metrics)

        # Required groups should be the same across all metrics.
        required_groups = metrics[0].required_groups

        # Collect union of all groups seen across runs.
        all_groups = set()
        for metric in metrics:
            all_groups.update(metric.groups_in_plan)

        return cls(
            percentage_targeting_required_groups=round(mean_percentage, 1),
            required_groups=required_groups,
            groups_in_plan=sorted(all_groups),
        )

    def to_numeric_score(self) -> float:
        pct = self.percentage_targeting_required_groups
        if 70.0 <= pct <= 90.0:
            return 100.0 - abs(pct - 80.0)
        else:
            if pct < 70.0:
                return max(0.0, 70.0 - (70.0 - pct) * 2.0)
            else:
                return max(0.0, 70.0 - (pct - 90.0) * 2.0)


class MuscleGroupCoverage(_base.Evaluator[MuscleGroupCoverageMetric]):
    name = "Muscle group coverage"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of exercise sets whose primary muscle group matches requirements.
- This should be in the range 70-90%.
- A score of less than 70% means the wrong muscle groups are being targeted too much.
- A score of greater than 90% means the class is not varied enough
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
class EquipmentUtilizationMetric(_base.Metric):
    percentage_utilized: float
    available_equipment: list[exercises.Equipment]
    used_equipment: list[exercises.Equipment]

    def render(self) -> str:
        return f"{self.percentage_utilized}% (available: {self.available_equipment}, used: {self.used_equipment})"

    @classmethod
    def aggregate(
        cls, metrics: list[EquipmentUtilizationMetric]
    ) -> EquipmentUtilizationMetric:
        if not metrics:
            raise ValueError("Cannot aggregate empty metrics list")

        mean_percentage = sum(m.percentage_utilized for m in metrics) / len(metrics)

        # Available equipment should be the same across all metrics.
        available_equipment = metrics[0].available_equipment

        # Collect union of all equipment used across runs.
        all_used = set()
        for metric in metrics:
            all_used.update(metric.used_equipment)

        return cls(
            percentage_utilized=round(mean_percentage, 1),
            available_equipment=available_equipment,
            used_equipment=sorted(all_used),
        )

    def to_numeric_score(self) -> float:
        return self.percentage_utilized


class EquipmentUtilization(_base.Evaluator[EquipmentUtilizationMetric]):
    name = "Equipment utilization"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of available equipment actually used in the plan.
- If just one or two pieces of equipment are available, this should be 100%.
- If more than two pieces of equipment are available, this can be less than 100%.
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
