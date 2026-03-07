from ._base import (
    Evaluation,
    EvaluationCategory,
    EvaluationDeps,
    GeneratedLessonPlanEvaluation,
)
from ._constants import get_evaluation_requirements
from ._evaluate import _evaluate_generated_lesson_plan, evaluate_system_prompt
from ._requirements_compliance import (
    DifficultyScore,
    DifficultyScoreMetric,
    DurationCompliance,
    DurationComplianceMetric,
    EquipmentConsistencyComplianceMetric,
    EquipmentUtilization,
    EquipmentUtilizationMetric,
    MuscleGroupCoverage,
    MuscleGroupCoverageMetric,
    MuscleGroupFocusComplianceMetric,
    StartingPositionConsistencyComplianceMetric,
    VariantOrderingComplianceMetric,
)
from ._structural_quality import (
    EquipmentConsistencyCompliance,
    MuscleGroupFocusCompliance,
    ProgressiveDifficulty,
    ProgressiveDifficultyMetric,
    SectionBalance,
    SectionBalanceMetric,
    StartingPositionConsistencyCompliance,
    TransitionQuality,
    TransitionQualityMetric,
    VariantOrderingCompliance,
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
