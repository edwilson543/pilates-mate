from pilates.domain import exercises
from pilates.domain.lesson_plans import _evaluation
from testing.helpers import exercises as exercises_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers

from . import get_evaluation_deps


class TestExerciseValidity:
    def test_fully_valid_when_all_exercises_in_generated_plan_exist(self):
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build()
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        exercises = [
            lesson_plan_helpers.GeneratedExercise.from_generated_exercise(exercise)
            for exercise in generated_plan.exercises
        ]
        deps = get_evaluation_deps(exercises=exercises)

        evaluator = _evaluation.ExerciseValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_exercises == 100.0
        assert result.invalid_exercises == []

    def test_not_fully_valid_when_generated_plan_features_non_existent_exercise(self):
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build()
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        exercises = [
            lesson_plan_helpers.GeneratedExercise.from_generated_exercise(exercise)
            for exercise in generated_plan.exercises
        ]
        # Exclude one of the exercises from the database.
        deps = get_evaluation_deps(exercises=exercises[:-1])

        evaluator = _evaluation.ExerciseValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_exercises == 89.0
        assert result.invalid_exercises == generated_plan.exercises[-1:]


class TestEquipmentValidity:
    def test_fully_valid_when_all_equipment_available(self):
        available_equipment = [exercises.Equipment.BALL, exercises.Equipment.BAND]
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            available_equipment=available_equipment
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

        evaluator = _evaluation.EquipmentValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan,
            requirements=requirements,
            deps=get_evaluation_deps(),
        )

        assert result.percentage_of_valid_equipment == 100.0
        assert result.invalid_equipment == []

    def test_not_fully_valid_when_unavailable_equipment_used(self):
        requirements = lesson_plan_helpers.LessonPlanRequirements.build(
            available_equipment=[exercises.Equipment.BALL]
        )
        set_with_ball = lesson_plan_helpers.GeneratedExerciseSet(
            equipment_variant=[exercises.Equipment.BALL]
        )
        set_with_ring = lesson_plan_helpers.GeneratedExerciseSet(
            equipment_variant=[exercises.Equipment.RING]
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_with_ball, set_with_ring]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )

        evaluator = _evaluation.EquipmentValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan,
            requirements=requirements,
            deps=get_evaluation_deps(),
        )

        assert result.percentage_of_valid_equipment == 50.0
        assert result.invalid_equipment == [exercises.Equipment.RING]


class TestMovementVariantValidity:
    def test_fully_valid_when_all_variants_correct(self):
        exercise = exercises_helpers.Exercise.build(
            id=1,
            movement_variants=[
                exercises.MovementVariant.STANDARD,
                exercises.MovementVariant.PULSE,
            ],
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=exercise.name
        )
        set_standard = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            movement_variant=exercises.MovementVariant.STANDARD,
        )
        set_pulse = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            movement_variant=exercises.MovementVariant.PULSE,
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_standard, set_pulse]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps(exercises=[exercise])

        evaluator = _evaluation.MovementVariantValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_variants == 100.0
        assert result.invalid_sets == []

    def test_not_fully_valid_when_invalid_variant_used(self):
        exercise = exercises_helpers.Exercise.build(
            id=1,
            movement_variants=[exercises.MovementVariant.STANDARD],
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=exercise.name
        )
        set_standard = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            movement_variant=exercises.MovementVariant.STANDARD,
        )
        set_pulse = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            movement_variant=exercises.MovementVariant.PULSE,
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_standard, set_pulse]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps(exercises=[exercise])

        evaluator = _evaluation.MovementVariantValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_variants == 50.0
        assert len(result.invalid_sets) == 1
        assert result.invalid_sets[0] == (
            generated_exercise,
            exercises.MovementVariant.PULSE,
        )


class TestEquipmentVariantValidity:
    def test_fully_valid_when_all_equipment_variants_correct(self):
        exercise = exercises_helpers.Exercise.build(
            id=1,
            equipment_variants=[exercises.Equipment.BALL, exercises.Equipment.BAND],
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=exercise.name
        )
        set_with_ball = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            equipment_variant=[exercises.Equipment.BALL],
        )
        set_no_equipment = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            equipment_variant=[],
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_with_ball, set_no_equipment]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps(exercises=[exercise])

        evaluator = _evaluation.EquipmentVariantValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_equipment_variants == 100.0
        assert result.invalid_sets == []

    def test_not_fully_valid_when_invalid_equipment_for_exercise(self):
        exercise = exercises_helpers.Exercise.build(
            id=1,
            equipment_variants=[exercises.Equipment.BALL],
        )
        generated_exercise = lesson_plan_helpers.GeneratedExercise(
            id=1, name=exercise.name
        )
        set_with_ball = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            equipment_variant=[exercises.Equipment.BALL],
        )
        set_with_ring = lesson_plan_helpers.GeneratedExerciseSet(
            exercise=generated_exercise,
            equipment_variant=[exercises.Equipment.RING],
        )
        sequence = lesson_plan_helpers.GeneratedExerciseSequence(
            sets=[set_with_ball, set_with_ring]
        )
        generated_plan = lesson_plan_helpers.GeneratedLessonPlan.build(
            warm_up=[sequence]
        )
        requirements = lesson_plan_helpers.LessonPlanRequirements()
        deps = get_evaluation_deps(exercises=[exercise])

        evaluator = _evaluation.EquipmentVariantValidity()
        result = evaluator.evaluate(
            generated_plan=generated_plan, requirements=requirements, deps=deps
        )

        assert result.percentage_of_valid_equipment_variants == 50.0
        assert len(result.invalid_sets) == 1
        assert result.invalid_sets[0] == (
            generated_exercise,
            [exercises.Equipment.RING],
        )
