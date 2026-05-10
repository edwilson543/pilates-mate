from __future__ import annotations

import attrs

from pilates.domain import exercises
from pilates.domain.lesson_plans import _generation, _models

from . import _base


@attrs.frozen
class ExerciseValidityMetric(_base.Metric):
    percentage_of_valid_exercises: float
    invalid_exercises: list[_generation.GeneratedExercise]

    def render(self) -> str:
        if not self.invalid_exercises:
            return f"{self.percentage_of_valid_exercises}%"
        invalids = ", ".join(
            f"{exercise.name} ({exercise.id})" for exercise in self.invalid_exercises
        )
        return f"{self.percentage_of_valid_exercises}% ({len(self.invalid_exercises)} invalid exercises: {invalids})"

    @classmethod
    def _aggregate(
        cls, metrics: list[ExerciseValidityMetric]
    ) -> ExerciseValidityMetric:
        mean_percentage = sum(m.percentage_of_valid_exercises for m in metrics) / len(
            metrics
        )

        # Collect all unique invalid exercises across all runs.
        seen_invalid = set()
        all_invalid = []
        for metric in metrics:
            for exercise in metric.invalid_exercises:
                key = (exercise.id, exercise.name)
                if key not in seen_invalid:
                    seen_invalid.add(key)
                    all_invalid.append(exercise)

        return cls(
            percentage_of_valid_exercises=round(mean_percentage, 1),
            invalid_exercises=all_invalid,
        )

    def to_numeric_score(self) -> float:
        if self.percentage_of_valid_exercises == 100.0:
            return 100.0
        else:
            return max(0.0, (self.percentage_of_valid_exercises - 90.0) * 10.0)


class ExerciseValidity(_base.Evaluator[ExerciseValidityMetric]):
    name = "Exercise validity"
    category = _base.EvaluationCategory.VALIDATION
    description = """Evaluation of whether the exercises included in the generated plan actually exist in the exercise bank.
- 100% of exercises should be valid.
- Any invalid exercises will be listed.
Note that if the same invalid exercises appears multiple times in the plan, this metric penalises it every
time it is used.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> ExerciseValidityMetric:
        exercise_bank = {
            exercise.id: exercise.name.lower()
            for exercise in deps.exercises_repo.get_exercises()
        }

        valid_exercises = []
        invalid_exercises = []

        for generated_exercise in generated_plan.exercises:
            if generated_exercise.id not in exercise_bank:
                invalid_exercises.append(generated_exercise)
            elif (
                exercise_bank[generated_exercise.id] != generated_exercise.name.lower()
            ):
                invalid_exercises.append(generated_exercise)
            else:
                valid_exercises.append(generated_exercise)

        return ExerciseValidityMetric(
            percentage_of_valid_exercises=round(
                100 * len(valid_exercises) / len(generated_plan.exercises)
            ),
            invalid_exercises=invalid_exercises,
        )


@attrs.frozen
class EquipmentValidityMetric(_base.Metric):
    percentage_of_valid_equipment: float
    invalid_equipment: list[exercises.Equipment]

    def render(self) -> str:
        if not self.invalid_equipment:
            return f"{self.percentage_of_valid_equipment}%"
        return f"{self.percentage_of_valid_equipment}% ({len(self.invalid_equipment)} invalid equipment: {self.invalid_equipment})"

    @classmethod
    def _aggregate(
        cls, metrics: list[EquipmentValidityMetric]
    ) -> EquipmentValidityMetric:
        mean_percentage = sum(m.percentage_of_valid_equipment for m in metrics) / len(
            metrics
        )

        # Collect unique invalid equipment across all runs.
        all_invalid = set()
        for metric in metrics:
            all_invalid.update(metric.invalid_equipment)

        return cls(
            percentage_of_valid_equipment=round(mean_percentage, 1),
            invalid_equipment=sorted(all_invalid),
        )

    def to_numeric_score(self) -> float:
        if self.percentage_of_valid_equipment == 100.0:
            return 100.0
        else:
            return max(0.0, (self.percentage_of_valid_equipment - 90.0) * 10.0)


class EquipmentValidity(_base.Evaluator[EquipmentValidityMetric]):
    name = "Equipment validity"
    category = _base.EvaluationCategory.VALIDATION
    description = """Validates that all equipment used in the plan is available according to requirements.
- 100% of equipment should be valid.
- Any invalid equipment will be listed.
Note that if the same invalid equipment appears multiple times in the plan, this metric penalises it every
time it is used.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> EquipmentValidityMetric:
        available_equipment_set = set(requirements.available_equipment)

        valid_count = 0
        invalid_count = 0
        invalid_equipment_set = set()

        for set_item in generated_plan.sets:
            for equipment in set_item.equipment_variant:
                if equipment in available_equipment_set:
                    valid_count += 1
                else:
                    invalid_count += 1
                    invalid_equipment_set.add(equipment)

        total_count = valid_count + invalid_count
        if total_count == 0:
            percentage = 100.0
        else:
            percentage = round(100 * valid_count / total_count)

        return EquipmentValidityMetric(
            percentage_of_valid_equipment=percentage,
            invalid_equipment=sorted(invalid_equipment_set),
        )


@attrs.frozen
class MovementVariantValidityMetric(_base.Metric):
    percentage_of_valid_variants: float
    invalid_sets: list[tuple[_generation.GeneratedExercise, exercises.MovementVariant]]

    def render(self) -> str:
        if not self.invalid_sets:
            return f"{self.percentage_of_valid_variants}%"
        return f"{self.percentage_of_valid_variants}% ({len(self.invalid_sets)} invalid movement variants)"

    @classmethod
    def _aggregate(
        cls, metrics: list[MovementVariantValidityMetric]
    ) -> MovementVariantValidityMetric:
        mean_percentage = sum(m.percentage_of_valid_variants for m in metrics) / len(
            metrics
        )

        # Collect unique invalid sets across all runs.
        seen_invalid = set()
        all_invalid = []
        for metric in metrics:
            for exercise, variant in metric.invalid_sets:
                key = (exercise.id, exercise.name, variant)
                if key not in seen_invalid:
                    seen_invalid.add(key)
                    all_invalid.append((exercise, variant))

        return cls(
            percentage_of_valid_variants=round(mean_percentage, 1),
            invalid_sets=all_invalid,
        )

    def to_numeric_score(self) -> float:
        if self.percentage_of_valid_variants == 100.0:
            return 100.0
        else:
            return max(0.0, (self.percentage_of_valid_variants - 90.0) * 10.0)


class MovementVariantValidity(_base.Evaluator[MovementVariantValidityMetric]):
    name = "Movement variant validity"
    category = _base.EvaluationCategory.VALIDATION
    description = """Validates that movement variants used for each exercise are valid according to the exercise bank.
- 100% should be valid.
- Any sets with invalid movement variants will be counted.
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> MovementVariantValidityMetric:
        exercise_lookup = deps.build_exercise_lookup()

        valid_count = 0
        invalid_sets = []

        for set_item in generated_plan.sets:
            exercise = exercise_lookup.get(set_item.exercise.id)
            if exercise is None:
                # Exercise doesn't exist, skip (handled by ExerciseValidity).
                continue

            if set_item.movement_variant in exercise.movement_variants:
                valid_count += 1
            else:
                invalid_sets.append((set_item.exercise, set_item.movement_variant))

        total_count = valid_count + len(invalid_sets)
        if total_count == 0:
            percentage = 100.0
        else:
            percentage = round(100 * valid_count / total_count)

        return MovementVariantValidityMetric(
            percentage_of_valid_variants=percentage,
            invalid_sets=invalid_sets,
        )


@attrs.frozen
class EquipmentVariantValidityMetric(_base.Metric):
    percentage_of_valid_equipment_variants: float
    invalid_sets: list[tuple[_generation.GeneratedExercise, list[exercises.Equipment]]]

    def render(self) -> str:
        if not self.invalid_sets:
            return f"{self.percentage_of_valid_equipment_variants}%"
        return f"{self.percentage_of_valid_equipment_variants}% ({len(self.invalid_sets)} invalid equipment variants)"

    @classmethod
    def _aggregate(
        cls, metrics: list[EquipmentVariantValidityMetric]
    ) -> EquipmentVariantValidityMetric:
        mean_percentage = sum(
            m.percentage_of_valid_equipment_variants for m in metrics
        ) / len(metrics)

        # Collect unique invalid sets across all runs.
        seen_invalid = set()
        all_invalid = []
        for metric in metrics:
            for exercise, equipment_list in metric.invalid_sets:
                key = (exercise.id, exercise.name, tuple(sorted(equipment_list)))
                if key not in seen_invalid:
                    seen_invalid.add(key)
                    all_invalid.append((exercise, equipment_list))

        return cls(
            percentage_of_valid_equipment_variants=round(mean_percentage, 1),
            invalid_sets=all_invalid,
        )

    def to_numeric_score(self) -> float:
        if self.percentage_of_valid_equipment_variants == 100.0:
            return 100.0
        else:
            return max(0.0, (self.percentage_of_valid_equipment_variants - 90.0) * 10.0)


class EquipmentVariantValidity(_base.Evaluator[EquipmentVariantValidityMetric]):
    name = "Equipment variant validity"
    category = _base.EvaluationCategory.VALIDATION
    description = """Validates that equipment variants used for each exercise are valid according to the exercise bank.
- 100% should be valid.
- Any sets with invalid equipment for the exercise will be counted.
Note: empty list is always valid (no equipment).
"""

    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _models.LessonPlanRequirements,
        deps: _base.EvaluationDeps,
    ) -> EquipmentVariantValidityMetric:
        exercise_lookup = deps.build_exercise_lookup()

        valid_count = 0
        invalid_sets = []

        for set_item in generated_plan.sets:
            exercise = exercise_lookup.get(set_item.exercise.id)
            if exercise is None:
                # Exercise doesn't exist, skip (handled by ExerciseValidity).
                continue

            # Empty equipment list is always valid.
            if not set_item.equipment_variant:
                valid_count += 1
                continue

            # Check if all equipment in the variant is valid for this exercise.
            all_valid = all(
                equipment in exercise.equipment_variants
                for equipment in set_item.equipment_variant
            )

            if all_valid:
                valid_count += 1
            else:
                invalid_sets.append((set_item.exercise, set_item.equipment_variant))

        total_count = valid_count + len(invalid_sets)
        if total_count == 0:
            percentage = 100.0
        else:
            percentage = round(100 * valid_count / total_count)

        return EquipmentVariantValidityMetric(
            percentage_of_valid_equipment_variants=percentage,
            invalid_sets=invalid_sets,
        )
