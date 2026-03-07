from __future__ import annotations

import abc
import enum
import typing

import attrs

from pilates.domain import exercises, templates, vendors

from .. import _generation, _repository


class EvaluationCategory(enum.StrEnum):
    VALIDATION = "VALIDATION"
    REQUIREMENTS_COMPLIANCE = "REQUIREMENTS_COMPLIANCE"
    STRUCTURAL_QUALITY = "STRUCTURAL_QUALITY"


class Metric(abc.ABC):
    """Base class for all evaluation metrics."""

    @abc.abstractmethod
    def render(self) -> str:
        """Render this metric as a human-readable string."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def aggregate(cls, metrics: list[typing.Self]) -> typing.Self:
        """
        Aggregate multiple metrics of this type into a single metric.

        :raises ValueError: If the metrics list is empty.
        """
        raise NotImplementedError


@attrs.frozen
class Evaluation:
    name: str
    category: EvaluationCategory
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
        evaluations_by_category: dict[EvaluationCategory, list[Evaluation]] = {
            category: [] for category in EvaluationCategory
        }
        for evaluation in self.evaluations:
            evaluations_by_category[evaluation.category].append(evaluation)

        return templates.render(
            directory="evaluation",
            filename="lesson-plan-evaluation.jinja",
            variables={"evaluations_by_category": evaluations_by_category},
        )


@attrs.frozen
class EvaluationDeps:
    completions_client: vendors.CompletionClient
    exercises_repo: exercises.Repository
    lesson_plan_repo: _repository.Repository


MetricT = typing.TypeVar("MetricT")


class Evaluator[MetricT](abc.ABC):
    """
    Evaluate the generated lesson plan against a particular metric.
    """

    name: typing.ClassVar[str]
    category: typing.ClassVar[EvaluationCategory]
    description: typing.ClassVar[str]

    @abc.abstractmethod
    def evaluate(
        self,
        generated_plan: _generation.GeneratedLessonPlan,
        requirements: _generation.LessonPlanRequirements,
        deps: EvaluationDeps,
    ) -> MetricT:
        raise NotImplementedError


# Helpers.


def build_exercise_lookup(
    exercises_repo: exercises.Repository,
) -> dict[int, exercises.Exercise]:
    """Build a lookup dict of exercise ID to Exercise for validation."""
    return {exercise.id: exercise for exercise in exercises_repo.get_exercises()}


def correlation_coefficient(
    actual: list[float],
    ideal: list[float],
) -> float:
    """Calculate Pearson correlation coefficient between two distributions."""
    if len(actual) != len(ideal) or len(actual) == 0:
        return 0.0

    n = len(actual)
    mean_actual = sum(actual) / n
    mean_ideal = sum(ideal) / n

    numerator = sum((a - mean_actual) * (i - mean_ideal) for a, i in zip(actual, ideal))
    denominator_actual = sum((a - mean_actual) ** 2 for a in actual)
    denominator_ideal = sum((i - mean_ideal) ** 2 for i in ideal)

    if denominator_actual == 0 or denominator_ideal == 0:
        return 0.0

    return numerator / (denominator_actual * denominator_ideal) ** 0.5
