from ._base import (
    Evaluation,
    EvaluationCategory,
    EvaluationDeps,
    Evaluator,
    GeneratedLessonPlanEvaluation,
    Metric,
)
from ._evaluate import evaluate_generated_lesson_plan
from ._requirements_compliance import (
    DifficultyScore,
    DifficultyScoreMetric,
    DurationCompliance,
    EquipmentUtilization,
    EquipmentUtilizationMetric,
    MuscleGroupCoverage,
    MuscleGroupCoverageMetric,
    PercentageMetric,
    SectionBalance,
    SectionBalanceMetric,
)
from ._validity import (
    EquipmentValidity,
    EquipmentValidityMetric,
    EquipmentVariantValidity,
    EquipmentVariantValidityMetric,
    ExerciseValidity,
    ExerciseValidityMetric,
    MovementVariantValidity,
    MovementVariantValidityMetric,
)


__all__ = [
    # Base types.
    "Evaluation",
    "EvaluationCategory",
    "EvaluationDeps",
    "Evaluator",
    "GeneratedLessonPlanEvaluation",
    "Metric",
    # Main entrypoint.
    "evaluate_generated_lesson_plan",
    # Validation evaluators.
    "ExerciseValidity",
    "ExerciseValidityMetric",
    "EquipmentValidity",
    "EquipmentValidityMetric",
    "MovementVariantValidity",
    "MovementVariantValidityMetric",
    "EquipmentVariantValidity",
    "EquipmentVariantValidityMetric",
    # Requirements compliance evaluators.
    "PercentageMetric",
    "DurationCompliance",
    "DifficultyScore",
    "DifficultyScoreMetric",
    "MuscleGroupCoverage",
    "MuscleGroupCoverageMetric",
    "SectionBalance",
    "SectionBalanceMetric",
    "EquipmentUtilization",
    "EquipmentUtilizationMetric",
]
