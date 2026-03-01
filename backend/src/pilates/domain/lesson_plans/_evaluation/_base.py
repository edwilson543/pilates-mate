from __future__ import annotations

import abc
import enum
import typing

import attrs

from pilates.domain import exercises, templates

from .. import _generation, _repository


class EvaluationCategory(enum.StrEnum):
    VALIDATION = "VALIDATION"
    REQUIREMENTS_COMPLIANCE = "REQUIREMENTS_COMPLIANCE"


class Metric(abc.ABC):
    """Base class for all evaluation metrics."""

    @abc.abstractmethod
    def render(self) -> str:
        """Render this metric as a human-readable string."""
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
