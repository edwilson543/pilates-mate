from __future__ import annotations

import abc
import enum
import typing

import attrs

from pilates.domain import exercises, vendors

from ... import _generation, _repository


@attrs.frozen
class EvaluationDeps:
    completions_client: vendors.CompletionClient
    exercises_repo: exercises.Repository
    lesson_plan_repo: _repository.Repository

    def build_exercise_lookup(
        self,
    ) -> dict[int, exercises.Exercise]:
        return {
            exercise.id: exercise for exercise in self.exercises_repo.get_exercises()
        }


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

    @abc.abstractmethod
    def to_numeric_score(self) -> float:
        """
        Convert this metric to a normalized numeric score.

        Returns a float where:
        - 0.0 represents worst possible performance
        - 100.0 represents ideal performance
        - Values can exceed 100.0 if applicable

        Each metric type implements its own semantics:
        - Higher is better (validity, most compliance)
        - Lower is better (transition rate)
        - Closer to target (duration, difficulty, muscle groups)
        """
        raise NotImplementedError


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
