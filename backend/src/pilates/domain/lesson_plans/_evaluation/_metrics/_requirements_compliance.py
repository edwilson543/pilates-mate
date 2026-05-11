from __future__ import annotations

import typing

import attrs

from pilates.domain import exercises
from pilates.domain.lesson_plans import _generation, _models

from . import _base, _helpers


@attrs.frozen
class PercentageMetric(_base.Metric):
    """
    Base class for percentage-based metrics.
    """

    value: float

    def render(self) -> str:
        return f"{self.value}%"

    def to_numeric_score(self) -> float:
        return self.value

    @classmethod
    def _aggregate(cls, metrics: list[PercentageMetric]) -> PercentageMetric:
        mean_value = sum(m.value for m in metrics) / len(metrics)
        return cls(value=round(mean_value, 3))


class DurationComplianceMetric(PercentageMetric): ...


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
        requirements: _models.LessonPlanRequirements,
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
        return f"{self.percentage_of_target}% (generated: {self.generated_score}, target: {self.target_score})"

    @classmethod
    def _aggregate(cls, metrics: list[DifficultyScoreMetric]) -> DifficultyScoreMetric:
        mean_generated_score = sum(m.generated_score for m in metrics) / len(metrics)
        mean_target_score = sum(m.target_score for m in metrics) / len(metrics)
        percentage = 100 * mean_generated_score / mean_target_score

        return cls(
            generated_score=round(mean_generated_score, 2),
            target_score=round(mean_target_score, 2),
            percentage_of_target=round(percentage, 1),
        )

    def to_numeric_score(self) -> float:
        return self.percentage_of_target


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
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> DifficultyScoreMetric:
        generated_score = self._get_difficulty_score_for_generated_plan(
            generated_plan, deps
        )
        target_score = _helpers.difficulty_score(requirements.target_difficulty)
        percentage = 100 * generated_score / target_score

        return DifficultyScoreMetric(
            generated_score=round(generated_score, 2),
            target_score=round(target_score, 2),
            percentage_of_target=round(percentage, 1),
        )

    def _get_difficulty_score_for_generated_plan(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        deps: _base.EvaluationDeps,
    ) -> float:
        """
        Multiply the difficulty score of each exercise by the percent of the plan spent doing that exercise.
        """
        exercise_lookup = deps.build_exercise_lookup()
        total_weighted_difficulty = 0.0

        for exercise_sequence in generated_plan.sequences:
            for exercise_set in exercise_sequence.sets:
                if not (exercise := exercise_lookup.get(exercise_set.exercise.id)):
                    continue

                difficulty_score = _helpers.difficulty_score(exercise.difficulty)
                duration_seconds = (
                    exercise_set.duration_seconds * exercise_sequence.reps
                )

                percent_plan_spent_doing_exercise = (
                    duration_seconds / generated_plan.duration_seconds
                )

                total_weighted_difficulty += (
                    difficulty_score * percent_plan_spent_doing_exercise
                )

        return total_weighted_difficulty


@attrs.frozen
class MuscleGroupCoverageMetric(_base.Metric):
    percentage_focused: float
    required_groups: list[exercises.MuscleGroup]
    groups_in_plan: list[exercises.MuscleGroup]

    def render(self) -> str:
        return f"Percent reps targeting muscle groups: {self.percentage_focused}% (required: {self.required_groups}, in plan: {self.groups_in_plan})"

    @classmethod
    def _aggregate(
        cls, metrics: list[MuscleGroupCoverageMetric]
    ) -> MuscleGroupCoverageMetric:
        mean_percentage = sum(m.percentage_focused for m in metrics) / len(metrics)
        required_groups = {
            group for metric in metrics for group in metric.required_groups
        }
        groups_in_plan = {
            group for metric in metrics for group in metric.groups_in_plan
        }

        return cls(
            percentage_focused=round(mean_percentage, 1),
            required_groups=sorted(required_groups),
            groups_in_plan=sorted(groups_in_plan),
        )

    def to_numeric_score(self) -> float:
        return self.percentage_focused


class MuscleGroupCoverage(_base.Evaluator[MuscleGroupCoverageMetric]):
    name = "Muscle group coverage"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of exercise reps whose primary muscle group matches requirements.
- This should be in the range 70-90%.
- A score of less than 70% means the wrong muscle groups are being targeted too much.
- A score of greater than 90% means the class is not varied enough
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> MuscleGroupCoverageMetric:
        exercise_lookup = deps.build_exercise_lookup()

        targeted_reps = 0
        targeted_groups: set[exercises.MuscleGroup] = set()

        for exercise_sequence in generated_plan.sequences:
            for exercise_set in exercise_sequence.sets:
                if not (exercise := exercise_lookup.get(exercise_set.exercise.id)):
                    continue

                if exercise.primary_muscle_group in requirements.target_muscle_groups:
                    targeted_reps += exercise_set.reps * exercise_sequence.reps

                targeted_groups.add(exercise.primary_muscle_group)

        percentage = 100 * targeted_reps / generated_plan.total_reps

        return MuscleGroupCoverageMetric(
            percentage_focused=round(percentage, 1),
            required_groups=sorted(requirements.target_muscle_groups),
            groups_in_plan=sorted(targeted_groups),
        )


@attrs.frozen
class EquipmentUtilisationMetric(_base.Metric):
    percentage_utilised: float
    available_equipment: list[exercises.Equipment]
    used_equipment: list[exercises.Equipment]

    def render(self) -> str:
        return f"{self.percentage_utilised}% (available: {self.available_equipment}, used: {self.used_equipment})"

    @classmethod
    def _aggregate(
        cls, metrics: list[EquipmentUtilisationMetric]
    ) -> EquipmentUtilisationMetric:
        mean_percentage = sum(m.percentage_utilised for m in metrics) / len(metrics)

        # Available equipment should be the same across all metrics.
        available_equipment = metrics[0].available_equipment

        # Collect union of all equipment used across runs.
        all_used = set()
        for metric in metrics:
            all_used.update(metric.used_equipment)

        return cls(
            percentage_utilised=round(mean_percentage, 1),
            available_equipment=available_equipment,
            used_equipment=sorted(all_used),
        )

    def to_numeric_score(self) -> float:
        return self.percentage_utilised

    @classmethod
    def no_available_equipment(cls) -> typing.Self:
        return cls(percentage_utilised=100.0, available_equipment=[], used_equipment=[])


class EquipmentUtilisation(_base.Evaluator[EquipmentUtilisationMetric]):
    name = "Equipment utilisation"
    category = _base.EvaluationCategory.REQUIREMENTS_COMPLIANCE
    description = """Percentage of available equipment actually used in the plan.
- If just one or two pieces of equipment are available, this should be 100%.
- If more than two pieces of equipment are available, this can be less than 100%.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> EquipmentUtilisationMetric:
        if not requirements.available_equipment:
            return EquipmentUtilisationMetric.no_available_equipment()

        used_equipment = {
            equipment
            for exercise_set in generated_plan.sets
            for equipment in exercise_set.equipment_variant
        }
        percentage_used = (
            100 * len(used_equipment) / len(requirements.available_equipment)
        )

        return EquipmentUtilisationMetric(
            percentage_utilised=round(percentage_used, 1),
            available_equipment=sorted(requirements.available_equipment),
            used_equipment=sorted(used_equipment),
        )
