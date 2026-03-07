from __future__ import annotations

from .. import _generation
from . import _base, _requirements_compliance, _structural_quality, _validity


def evaluate_generated_lesson_plan(
    *,
    generated_plan: _generation.GeneratedLessonPlan,
    requirements: _generation.LessonPlanRequirements,
    deps: _base.EvaluationDeps,
) -> _base.GeneratedLessonPlanEvaluation:
    evaluators = [
        # Validation.
        _validity.ExerciseValidity(),
        _validity.EquipmentValidity(),
        _validity.MovementVariantValidity(),
        _validity.EquipmentVariantValidity(),
        # Requirements compliance.
        _requirements_compliance.DurationCompliance(),
        _requirements_compliance.DifficultyScore(),
        _requirements_compliance.MuscleGroupCoverage(),
        _requirements_compliance.EquipmentUtilization(),
        # Structural quality.
        _structural_quality.SectionBalance(),
        _structural_quality.TransitionQuality(),
        _structural_quality.ProgressiveDifficulty(),
        _structural_quality.VariantOrderingCompliance(),
        _structural_quality.EquipmentConsistencyCompliance(),
        _structural_quality.MuscleGroupFocusCompliance(),
        _structural_quality.StartingPositionConsistencyCompliance(),
    ]

    evaluations: list[_base.Evaluation] = []

    for evaluator in evaluators:
        outcome = evaluator.evaluate(generated_plan, requirements, deps)
        evaluation = _base.Evaluation(
            name=evaluator.name,
            category=evaluator.category,
            description=evaluator.description,
            outcome=outcome,
        )
        evaluations.append(evaluation)

    return _base.GeneratedLessonPlanEvaluation(evaluations=evaluations)
