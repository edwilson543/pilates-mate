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


class LessonPlanRequirements(factory.Factory):
    class Meta:
        model = lesson_plans.LessonPlanRequirements

    duration_minutes = 30
    target_difficulty = exercises.Difficulty.INTERMEDIATE
    target_muscle_groups = factory.LazyFunction(lambda: [exercises.MuscleGroup.CORE])
    example_lesson_lan_ids = factory.ListFactory()
    user_prompt = factory.Sequence(lambda n: f"use-prompt-{n}")
    available_equipment = factory.LazyFunction(lambda: [exercises.Equipment.BALL])


class LessonPlan(factory.Factory):
    class Meta:
        model = lesson_plans.LessonPlan

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    date = factory.Sequence(lambda n: dt.date(2026, 1, 1) + dt.timedelta(days=n))
    requirements = factory.SubFactory(LessonPlanRequirements)
    status = lesson_plans.LessonPlanStatus.GENERATED
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
            for exercise_set in lesson_plan.exercise_sets:
                exercise = exercise_helpers.Exercise.insert(uow)
                exercise_set.exercise_id = exercise.id

        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name=lesson_plan.name,
            date=lesson_plan.date,
            requirements=lesson_plan.requirements,
        )

        for section, section_enum in [
            (lesson_plan.warm_up, lesson_plans.LessonPlanSection.WARM_UP),
            (lesson_plan.main_session, lesson_plans.LessonPlanSection.MAIN_SESSION),
            (lesson_plan.cool_down, lesson_plans.LessonPlanSection.COOL_DOWN),
        ]:
            for sequence in section:
                sequence_id = uow.lesson_plans.add_sequence_to_section(
                    lesson_plan_id=lesson_plan_id,
                    section=section_enum,
                    name=sequence.name,
                    reps=sequence.reps,
                    notes=sequence.notes,
                )
                for exercise_set in sequence.sets:
                    uow.lesson_plans.add_set_to_sequence(
                        sequence_id=sequence_id,
                        exercise_id=exercise_set.exercise_id,
                        reps=exercise_set.reps,
                        duration_seconds=exercise_set.duration_seconds,
                        movement_variant=exercise_set.movement_variant,
                        equipment_variant=exercise_set.equipment_variant,
                    )

        uow.lesson_plans.update_lesson_plan(
            lesson_plan_id,
            description=lesson_plan.description,
            status=lesson_plan.status,
        )

        return uow.lesson_plans.get_lesson_plan(lesson_plan_id)


class Evaluation(factory.Factory):
    class Meta:
        model = lesson_plans.Evaluation

    name = factory.Sequence(lambda n: f"Evaluation-{n}")
    category = lesson_plans.EvaluationCategory.VALIDATION
    description = factory.Sequence(lambda n: f"Description-{n}")
    outcome = factory.LazyFunction(dict)
