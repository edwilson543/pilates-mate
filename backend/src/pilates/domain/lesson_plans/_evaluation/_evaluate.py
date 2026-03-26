from __future__ import annotations

import asyncio
import collections
import typing

import attrs

from pilates.domain import templates

from .. import _generation
from . import _constants, _metrics


@attrs.frozen
class Evaluation:
    name: str
    category: _metrics.EvaluationCategory
    description: str
    outcome: typing.Any


@attrs.frozen
class GeneratedLessonPlanEvaluation:
    evaluations: list[Evaluation]

    @classmethod
    def aggregate(cls, evaluations: list[typing.Self]) -> typing.Self:
        """
        Aggregate multiple evaluations by calculating the mean of their metrics.

        This is mathematically invalid for some metrics, but provides a good enough measure.

        :raises ValueError: If the evaluations list is empty.
        """
        if not evaluations:
            raise ValueError("Cannot calculate mean of empty evaluations list")

        # Group evaluations by name (each name corresponds to one evaluator type).
        evaluations_by_name: dict[str, list[Evaluation]] = {}
        for evaluation in evaluations:
            for single_evaluation in evaluation.evaluations:
                if single_evaluation.name not in evaluations_by_name:
                    evaluations_by_name[single_evaluation.name] = []
                evaluations_by_name[single_evaluation.name].append(single_evaluation)

        # Aggregate each group of evaluations.
        aggregated_evaluations: list[Evaluation] = []
        for name, evaluation_group in evaluations_by_name.items():
            # Extract the outcome metrics from each evaluation.
            outcomes = [evaluation.outcome for evaluation in evaluation_group]

            # Get the metric class and call its aggregate method.
            metric_class = type(outcomes[0])
            aggregated_metric = metric_class.aggregate(outcomes)

            # Create a new evaluation with the aggregated metric.
            aggregated_evaluation = Evaluation(
                name=evaluation_group[0].name,
                category=evaluation_group[0].category,
                description=evaluation_group[0].description,
                outcome=aggregated_metric,
            )
            aggregated_evaluations.append(aggregated_evaluation)

        return cls(evaluations=aggregated_evaluations)

    def render(self) -> str:
        evaluations_by_category: dict[_metrics.EvaluationCategory, list[Evaluation]] = {
            category: [] for category in _metrics.EvaluationCategory
        }
        for evaluation in self.evaluations:
            evaluations_by_category[evaluation.category].append(evaluation)

        return templates.render(
            directory="evaluation",
            filename="lesson-plan-evaluation.jinja",
            variables={"evaluations_by_category": evaluations_by_category},
        )

    def to_numeric_score(self) -> float:
        """
        Calculate aggregate numeric score for optimization tracking.
        """
        evaluations_by_category: collections.defaultdict[
            _metrics.EvaluationCategory, list[Evaluation]
        ] = collections.defaultdict(list)
        for evaluation in self.evaluations:
            evaluations_by_category[evaluation.category].append(evaluation)

        def _mean(evals: list[Evaluation]) -> float:
            if not evals:
                return 0
            return sum(eval.outcome.to_numeric_score() for eval in evals) / len(evals)

        means = {
            category: _mean(evals)
            for category, evals in evaluations_by_category.items()
        }

        return (
            means.get(_metrics.EvaluationCategory.VALIDATION, 0) * 0.4
            + means.get(_metrics.EvaluationCategory.REQUIREMENTS_COMPLIANCE, 0) * 0.3
            + means.get(_metrics.EvaluationCategory.STRUCTURAL_QUALITY, 0) * 0.3
        )

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "numeric_score": self.to_numeric_score(),
            "evaluations": [
                {
                    "name": evaluation.name,
                    "category": str(evaluation.category),
                    "description": evaluation.description,
                    "numeric_score": evaluation.outcome.to_numeric_score(),
                    "outcome": evaluation.outcome.render(),
                }
                for evaluation in self.evaluations
            ],
        }


async def evaluate_system_prompt(
    *, version: str, deps: _metrics.EvaluationDeps
) -> GeneratedLessonPlanEvaluation:
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

    return GeneratedLessonPlanEvaluation.aggregate(evaluations)


def render_sample_system_prompt(*, version: str, deps: _metrics.EvaluationDeps) -> str:
    requirements = _constants.get_evaluation_requirements()[0]
    return _generation.get_system_prompt(
        requirements,
        deps.lesson_plan_repo,
        deps.exercises_repo,
        version=version,
    )


def evaluate_generated_lesson_plan(
    *,
    generated_plan: _generation.GeneratedLessonPlan,
    requirements: _generation.LessonPlanRequirements,
    deps: _metrics.EvaluationDeps,
) -> GeneratedLessonPlanEvaluation:
    evaluators = [
        # Validation.
        _metrics.ExerciseValidity(),
        _metrics.EquipmentValidity(),
        _metrics.MovementVariantValidity(),
        _metrics.EquipmentVariantValidity(),
        # Requirements compliance.
        _metrics.DurationCompliance(),
        _metrics.DifficultyScore(),
        _metrics.MuscleGroupCoverage(),
        _metrics.EquipmentUtilisation(),
        # Structural quality.
        _metrics.SectionBalance(),
        _metrics.TransitionQuality(),
        _metrics.ProgressiveDifficulty(),
        _metrics.VariantOrderingCompliance(),
        _metrics.EquipmentConsistencyCompliance(),
        _metrics.MuscleGroupFocusCompliance(),
        _metrics.StartingPositionConsistencyCompliance(),
    ]

    evaluations: list[Evaluation] = []

    for evaluator in evaluators:
        outcome = evaluator.evaluate(generated_plan, requirements, deps)
        evaluation = Evaluation(
            name=evaluator.name,
            category=evaluator.category,
            description=evaluator.description,
            outcome=outcome,
        )
        evaluations.append(evaluation)

    return GeneratedLessonPlanEvaluation(evaluations=evaluations)


async def _generate_and_evaluate(
    system_prompt: str,
    requirements: _generation.LessonPlanRequirements,
    deps: _metrics.EvaluationDeps,
) -> GeneratedLessonPlanEvaluation:
    generated_plan = await _generation.generate_lesson_plan(
        requirements=requirements,
        client=deps.completions_client,
        system_prompt=system_prompt,
    )

    return evaluate_generated_lesson_plan(
        generated_plan=generated_plan, requirements=requirements, deps=deps
    )
