import pytest

from pilates.domain import exercises
from pilates.domain.lesson_plans._evaluation._metrics import _requirements_compliance
from testing.helpers import exercises as exercises_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers
from tests.unit.domain.lesson_plans._evaluation import get_evaluation_deps


class TestDurationCompliance:
    @pytest.mark.parametrize(
        "target_duration, percentage", [(30, 100.0), (60, 50.0), (15, 200.0)]
    )
    def test_gets_correct_percentage_of_required_duration(
        self, target_duration: int, percentage: float
    ):
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            duration_minutes=target_duration
        )

        set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=60)
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(sets=[set], reps=10)
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence], main_session=[sequence], cool_down=[sequence]
        )

        evaluator = _requirements_compliance.DurationCompliance()
        result = evaluator.evaluate(
            generated_plan=generated_plan,
            requirements=requirements,
            deps=get_evaluation_deps(),
        )

        assert result.value == percentage


class TestDifficultyScore:
    def test_perfect_match_when_difficulties_align(self):
        beginner_exercise = exercises_helpers.Exercise.build(
            id=1, difficulty=exercises.Difficulty.BEGINNER
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            target_difficulty=exercises.Difficulty.BEGINNER
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=beginner_exercise.name
        )
        set = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise, duration_seconds=60
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(sets=[set], reps=10)
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        deps = get_evaluation_deps(exercises=[beginner_exercise])

        evaluator = _requirements_compliance.DifficultyScore()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.generated_score == 1.0
        assert result.target_score == 1.0
        assert result.percentage_of_target == 100.0

    def test_lower_percentage_when_plan_too_easy(self):
        beginner_exercise = exercises_helpers.Exercise.build(
            id=1, difficulty=exercises.Difficulty.BEGINNER
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            target_difficulty=exercises.Difficulty.ADVANCED
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=beginner_exercise.name
        )
        set = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise, duration_seconds=60
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(sets=[set], reps=10)
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        deps = get_evaluation_deps(exercises=[beginner_exercise])

        evaluator = _requirements_compliance.DifficultyScore()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.generated_score == 1.0
        assert result.target_score == 10.0
        assert result.percentage_of_target == 10.0

    def test_higher_percentage_when_plan_too_hard(self):
        advanced_exercise = exercises_helpers.Exercise.build(
            id=1, difficulty=exercises.Difficulty.ADVANCED
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            target_difficulty=exercises.Difficulty.BEGINNER
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=advanced_exercise.name
        )
        set = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise, duration_seconds=60
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(sets=[set], reps=10)
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        deps = get_evaluation_deps(exercises=[advanced_exercise])

        evaluator = _requirements_compliance.DifficultyScore()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.generated_score == 10.0
        assert result.target_score == 1.0
        assert result.percentage_of_target == 1000.0


class TestMuscleGroupCoverage:
    def test_high_coverage_when_most_exercises_target_required_groups(self):
        core_exercise = exercises_helpers.Exercise.build(
            id=1, primary_muscle_group=exercises.MuscleGroup.CORE
        )
        glutes_exercise = exercises_helpers.Exercise.build(
            id=2, primary_muscle_group=exercises.MuscleGroup.GLUTES
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            target_muscle_groups=[exercises.MuscleGroup.CORE]
        )
        core_gen = lesson_plan_helpers.GeneratedExercise(id=1, name=core_exercise.name)
        glutes_gen = lesson_plan_helpers.GeneratedExercise(
            id=2, name=glutes_exercise.name
        )
        core_set = lesson_plan_helpers.GeneratedExerciseSet(exercise=core_gen)
        glutes_set = lesson_plan_helpers.GeneratedExerciseSet(exercise=glutes_gen)
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[core_set, core_set, glutes_set]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence], main_session=[], cool_down=[]
        )
        deps = get_evaluation_deps(exercises=[core_exercise, glutes_exercise])

        evaluator = _requirements_compliance.MuscleGroupCoverage()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_targeting_required_groups == 66.7
        assert result.required_groups == [exercises.MuscleGroup.CORE]
        assert set(result.groups_in_plan) == {
            exercises.MuscleGroup.CORE,
            exercises.MuscleGroup.GLUTES,
        }

    def test_low_coverage_when_few_exercises_match(self):
        core_exercise = exercises_helpers.Exercise.build(
            id=1, primary_muscle_group=exercises.MuscleGroup.CORE
        )
        glutes_exercise = exercises_helpers.Exercise.build(
            id=2, primary_muscle_group=exercises.MuscleGroup.GLUTES
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            target_muscle_groups=[exercises.MuscleGroup.GLUTES]
        )
        core_gen = lesson_plan_helpers.GeneratedExercise(id=1, name=core_exercise.name)
        glutes_gen = lesson_plan_helpers.GeneratedExercise(
            id=2, name=glutes_exercise.name
        )
        core_set = lesson_plan_helpers.GeneratedExerciseSet(exercise=core_gen)
        glutes_set = lesson_plan_helpers.GeneratedExerciseSet(exercise=glutes_gen)
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[core_set, core_set, glutes_set]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence], main_session=[], cool_down=[]
        )
        deps = get_evaluation_deps(exercises=[core_exercise, glutes_exercise])

        evaluator = _requirements_compliance.MuscleGroupCoverage()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_targeting_required_groups == 33.3
        assert result.required_groups == [exercises.MuscleGroup.GLUTES]
        assert set(result.groups_in_plan) == {
            exercises.MuscleGroup.CORE,
            exercises.MuscleGroup.GLUTES,
        }


class TestEquipmentUtilization:
    def test_high_utilization_when_most_equipment_used(self):
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            available_equipment=[exercises.Equipment.BALL, exercises.Equipment.BAND]
        )
        set_with_ball = lesson_plan_helpers.GeneratedExerciseSet(
            equipment_variant=[exercises.Equipment.BALL]
        )
        set_with_band = lesson_plan_helpers.GeneratedExerciseSet(
            equipment_variant=[exercises.Equipment.BAND]
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_with_ball, set_with_band]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        deps = get_evaluation_deps()

        evaluator = _requirements_compliance.EquipmentUtilization()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_utilized == 100.0
        assert set(result.available_equipment) == {
            exercises.Equipment.BALL,
            exercises.Equipment.BAND,
        }
        assert set(result.used_equipment) == {
            exercises.Equipment.BALL,
            exercises.Equipment.BAND,
        }

    def test_low_utilization_when_little_equipment_used(self):
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            available_equipment=[
                exercises.Equipment.BALL,
                exercises.Equipment.BAND,
                exercises.Equipment.RING,
            ]
        )
        set_with_ball = lesson_plan_helpers.GeneratedExerciseSet(
            equipment_variant=[exercises.Equipment.BALL]
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(sets=[set_with_ball])
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        deps = get_evaluation_deps()

        evaluator = _requirements_compliance.EquipmentUtilization()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_utilized == 33.3
        assert result.used_equipment == [exercises.Equipment.BALL]


class TestDurationComplianceMetricScoring:
    def test_to_numeric_score_when_perfect(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=100.0)

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_within_ideal_range_lower(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=95.0)

        assert metric.to_numeric_score() == 75.0

    def test_to_numeric_score_when_within_ideal_range_upper(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=105.0)

        assert metric.to_numeric_score() == 75.0

    def test_to_numeric_score_when_at_acceptable_boundary(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=90.0)

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_outside_acceptable_range(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=80.0)

        assert metric.to_numeric_score() == 30.0

    def test_to_numeric_score_when_very_poor(self) -> None:
        metric = _requirements_compliance.DurationComplianceMetric(value=60.0)

        assert metric.to_numeric_score() == 0.0


class TestDifficultyScoreMetricScoring:
    def test_to_numeric_score_when_perfect_match(self) -> None:
        metric = _requirements_compliance.DifficultyScoreMetric(
            generated_score=5.0,
            target_score=5.0,
            percentage_of_target=100.0,
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_slightly_off(self) -> None:
        metric = _requirements_compliance.DifficultyScoreMetric(
            generated_score=4.5,
            target_score=5.0,
            percentage_of_target=90.0,
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_very_different(self) -> None:
        metric = _requirements_compliance.DifficultyScoreMetric(
            generated_score=2.0,
            target_score=5.0,
            percentage_of_target=40.0,
        )

        score = metric.to_numeric_score()
        assert score == 40.0


class TestMuscleGroupCoverageMetricScoring:
    def test_to_numeric_score_when_at_ideal_center(self) -> None:
        metric = _requirements_compliance.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=80.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_at_ideal_lower_bound(self) -> None:
        metric = _requirements_compliance.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=70.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_at_ideal_upper_bound(self) -> None:
        metric = _requirements_compliance.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=90.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 90.0

    def test_to_numeric_score_when_below_ideal_range(self) -> None:
        metric = _requirements_compliance.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=60.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 50.0

    def test_to_numeric_score_when_above_ideal_range(self) -> None:
        metric = _requirements_compliance.MuscleGroupCoverageMetric(
            percentage_targeting_required_groups=100.0,
            required_groups=[exercises.MuscleGroup.CORE],
            groups_in_plan=[exercises.MuscleGroup.CORE],
        )

        assert metric.to_numeric_score() == 50.0


class TestEquipmentUtilizationMetricScoring:
    def test_to_numeric_score_when_fully_utilized(self) -> None:
        metric = _requirements_compliance.EquipmentUtilizationMetric(
            percentage_utilized=100.0,
            available_equipment=[exercises.Equipment.BALL],
            used_equipment=[exercises.Equipment.BALL],
        )

        assert metric.to_numeric_score() == 100.0

    def test_to_numeric_score_when_partially_utilized(self) -> None:
        metric = _requirements_compliance.EquipmentUtilizationMetric(
            percentage_utilized=50.0,
            available_equipment=[exercises.Equipment.BALL],
            used_equipment=[],
        )

        assert metric.to_numeric_score() == 50.0
