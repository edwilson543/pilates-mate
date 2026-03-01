import pytest

from pilates.domain import exercises
from pilates.domain.lesson_plans import _evaluation
from testing.helpers import exercises as exercises_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers

from . import get_evaluation_deps


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

        evaluator = _evaluation.DurationCompliance()
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

        evaluator = _evaluation.DifficultyScore()
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

        evaluator = _evaluation.DifficultyScore()
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

        evaluator = _evaluation.DifficultyScore()
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

        evaluator = _evaluation.MuscleGroupCoverage()
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

        evaluator = _evaluation.MuscleGroupCoverage()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_targeting_required_groups == 33.3
        assert result.required_groups == [exercises.MuscleGroup.GLUTES]
        assert set(result.groups_in_plan) == {
            exercises.MuscleGroup.CORE,
            exercises.MuscleGroup.GLUTES,
        }


class TestSectionBalance:
    def test_high_correlation_when_ideal_distribution(self):
        # Create a plan with ideal distribution: 10% warm-up, 80% main, 10% cool-down.
        warm_up_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=60)
        main_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=480)
        cool_down_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=60)

        warm_up_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[warm_up_set], reps=1
        )
        main_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[main_set], reps=1
        )
        cool_down_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[cool_down_set], reps=1
        )

        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[warm_up_sequence],
            main_session=[main_sequence],
            cool_down=[cool_down_sequence],
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps()

        evaluator = _evaluation.SectionBalance()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.warm_up_percentage == 10.0
        assert result.main_session_percentage == 80.0
        assert result.cool_down_percentage == 10.0
        assert result.correlation_coefficient == pytest.approx(1.0, abs=0.01)

    def test_low_correlation_when_unbalanced(self):
        # Create an unbalanced plan: mostly warm-up.
        warm_up_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=500)
        main_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=50)
        cool_down_set = lesson_plan_helpers.GeneratedExerciseSet(duration_seconds=50)

        warm_up_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[warm_up_set], reps=1
        )
        main_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[main_set], reps=1
        )
        cool_down_sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[cool_down_set], reps=1
        )

        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[warm_up_sequence],
            main_session=[main_sequence],
            cool_down=[cool_down_sequence],
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps()

        evaluator = _evaluation.SectionBalance()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        # Should have poor correlation with ideal distribution.
        assert result.correlation_coefficient < 0.5


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

        evaluator = _evaluation.EquipmentUtilization()
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

        evaluator = _evaluation.EquipmentUtilization()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_utilized == 33.3
        assert result.used_equipment == [exercises.Equipment.BALL]
