from __future__ import annotations

import asyncio

from .. import _generation
from . import (
    _base,
    _constants,
    _requirements_compliance,
    _structural_quality,
    _validity,
)


async def evaluate_system_prompt(
    *, version: str, deps: _base.EvaluationDeps
) -> _base.GeneratedLessonPlanEvaluation:
    requirements_list = _constants.get_evaluation_requirements()

    evaluation_tasks = [
        _generate_and_evaluate(
            system_prompt=_generation.get_system_prompt(
                requirements,
                deps.lesson_plan_repo,
                deps.exercises_repo,
                version=version,
            ),
            requirements=requirements,
            deps=deps,
        )
        for requirements in requirements_list
    ]
    evaluations = await asyncio.gather(*evaluation_tasks)

    return _base.GeneratedLessonPlanEvaluation.aggregate(evaluations)


async def _generate_and_evaluate(
    system_prompt: str,
    requirements: _generation.LessonPlanRequirements,
    deps: _base.EvaluationDeps,
) -> _base.GeneratedLessonPlanEvaluation:
    generated_plan = await _generation.generate_lesson_plan(
        requirements=requirements,
        client=deps.completions_client,
        system_prompt=system_prompt,
    )

    return _evaluate_generated_lesson_plan(
        generated_plan=generated_plan, requirements=requirements, deps=deps
    )


def _evaluate_generated_lesson_plan(
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
