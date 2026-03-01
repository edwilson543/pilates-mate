import datetime as dt

import factory

from pilates.domain import exercises, lesson_plans, unit_of_work
from testing.helpers import exercises as exercise_helpers


class GeneratedExercise(factory.Factory):
    class Meta:
        model = lesson_plans.GeneratedExercise

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")

    @classmethod
    def from_generated_exercise(
        cls, exercise: lesson_plans.GeneratedExercise, **kwargs: object
    ) -> exercises.Exercise:
        return exercise_helpers.Exercise.build(
            id=exercise.id, name=exercise.name, **kwargs
        )


class GeneratedExerciseSet(factory.Factory):
    class Meta:
        model = lesson_plans.GeneratedExerciseSet

    exercise = factory.SubFactory(GeneratedExercise)
    reps = 10
    duration_seconds = 30
    movement_variant = exercises.MovementVariant.STANDARD
    equipment_variant = factory.ListFactory()


class GeneratedExerciseSequence(factory.Factory):
    class Meta:
        model = lesson_plans.GeneratedExerciseSequence
        exclude = ("n_sets",)

    n_sets = 3
    sets = factory.LazyAttribute(
        lambda o: [GeneratedExerciseSet() for _ in range(o.n_sets)]
    )

    name = factory.Sequence(lambda n: f"name-{n}")
    notes = factory.Sequence(lambda n: f"notes-{n}")
    reps = 1


class GeneratedLessonPlan(factory.Factory):
    class Meta:
        model = lesson_plans.GeneratedLessonPlan

    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    warm_up = factory.LazyFunction(lambda: [GeneratedExerciseSequence()])
    main_session = factory.LazyFunction(lambda: [GeneratedExerciseSequence()])
    cool_down = factory.LazyFunction(lambda: [GeneratedExerciseSequence()])


class ExerciseSet(factory.Factory):
    class Meta:
        model = lesson_plans.ExerciseSet
        exclude = ("exercise", "exercise_id_counter")

    id = factory.Sequence(lambda n: n)
    exercise_id = factory.Sequence(lambda n: n)
    reps = 10
    duration_seconds = 30
    movement_variant = exercises.MovementVariant.STANDARD
    equipment_variant = factory.ListFactory()


class ExerciseSequence(factory.Factory):
    class Meta:
        model = lesson_plans.ExerciseSequence
        exclude = ("n_sets",)

    id = factory.Sequence(lambda n: n)
    n_sets = 3
    sets = factory.LazyAttribute(lambda o: [ExerciseSet() for _ in range(o.n_sets)])

    name = factory.Sequence(lambda n: f"name-{n}")
    notes = factory.Sequence(lambda n: f"notes-{n}")
    reps = 1


class LessonPlan(factory.Factory):
    class Meta:
        model = lesson_plans.LessonPlan

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    date = factory.Sequence(lambda n: dt.date(2026, 1, 1) + dt.timedelta(days=n))
    warm_up = factory.LazyFunction(lambda: [ExerciseSequence()])
    main_session = factory.LazyFunction(lambda: [ExerciseSequence()])
    cool_down = factory.LazyFunction(lambda: [ExerciseSequence()])

    @classmethod
    def insert(
        cls,
        uow: unit_of_work.UnitOfWork,
        create_exercises: bool = True,
        **kwargs: object,
    ) -> lesson_plans.LessonPlan:
        lesson_plan = cls.create(**kwargs)

        # Create real exercises, otherwise the referenced `exercise_id`s will be invalid.
        if create_exercises:
            for set in lesson_plan.exercise_sets:
                exercise = exercise_helpers.Exercise.insert(uow)
                set.exercise_id = exercise.id

        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name=lesson_plan.name,
            description=lesson_plan.description,
            date=lesson_plan.date,
            warm_up=lesson_plan.warm_up,
            main_session=lesson_plan.main_session,
            cool_down=lesson_plan.cool_down,
        )
        lesson_plan.id = lesson_plan_id
        # TODO! set all exercise set / exercise sequence IDs correctly.
        # Currently they will just retain the factory-generated IDs.
        return lesson_plan


class LessonPlanRequirements(factory.Factory):
    class Meta:
        model = lesson_plans.LessonPlanRequirements

    duration_minutes = 30
    target_difficulty = exercises.Difficulty.INTERMEDIATE
    target_muscle_groups = factory.LazyFunction(lambda: [exercises.MuscleGroup.CORE])
    example_lesson_lan_ids = factory.ListFactory()
    user_prompt = factory.Sequence(lambda n: f"use-prompt-{n}")
    available_equipment = factory.LazyFunction(lambda: [exercises.Equipment.BALL])
