import datetime as dt

import factory

from pilates.application import generate_lesson_plan
from pilates.domain import lesson_planning


class GeneratedExercise(factory.Factory):
    class Meta:
        model = generate_lesson_plan._GeneratedExercise

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")


class GeneratedExerciseSet(factory.Factory):
    class Meta:
        model = generate_lesson_plan._GeneratedExerciseSet

    exercise = factory.SubFactory(GeneratedExercise)
    reps = 10
    duration_seconds = 30
    movement_variant = lesson_planning.MovementVariant.STANDARD


class GeneratedExerciseSequence(factory.Factory):
    class Meta:
        model = generate_lesson_plan._GeneratedExerciseSequence
        exclude = ("n_sets",)

    n_sets = 3
    sets = factory.LazyAttribute(
        lambda o: [GeneratedExerciseSet() for _ in range(o.n_sets)]
    )

    name = factory.Sequence(lambda n: f"name-{n}")
    notes = factory.Sequence(lambda n: f"notes-{n}")
    reps = 1


class Exercise(factory.Factory):
    class Meta:
        model = lesson_planning.Exercise

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    category = lesson_planning.ExerciseCategory.EFFORT
    difficulty = lesson_planning.Difficulty.INTERMEDIATE
    primary_muscle_group = lesson_planning.MuscleGroup.CORE
    starting_position = lesson_planning.StartingPosition.STANDING
    movement_variants = factory.LazyFunction(
        lambda: [lesson_planning.MovementVariant.STANDARD]
    )

    @classmethod
    def create_in_repo(
        cls, repo: lesson_planning.Repository, **kwargs: object
    ) -> lesson_planning.LessonPlan:
        exercise = cls.create(**kwargs)
        exercise_id = repo.create_exercise(
            name=exercise.name,
            description=exercise.description,
            category=exercise.category,
            difficulty=exercise.difficulty,
            primary_muscle_group=exercise.primary_muscle_group,
            starting_position=exercise.starting_position,
            movement_variants=exercise.movement_variants,
        )
        exercise.id = exercise_id
        return exercise


class ExerciseSet(factory.Factory):
    class Meta:
        model = lesson_planning.ExerciseSet

    id = factory.Sequence(lambda n: n)
    exercise = factory.SubFactory(Exercise)
    reps = 10
    duration_seconds = 30
    movement_variant = lesson_planning.MovementVariant.STANDARD


class ExerciseSequence(factory.Factory):
    class Meta:
        model = lesson_planning.ExerciseSequence
        exclude = ("n_sets",)

    id = factory.Sequence(lambda n: n)
    n_sets = 3
    sets = factory.LazyAttribute(lambda o: [ExerciseSet() for _ in range(o.n_sets)])

    name = factory.Sequence(lambda n: f"name-{n}")
    notes = factory.Sequence(lambda n: f"notes-{n}")
    reps = 1


class LessonPlan(factory.Factory):
    class Meta:
        model = lesson_planning.LessonPlan

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    date = factory.Sequence(lambda n: dt.date(2026, 1, 1) + dt.timedelta(days=n))
    warm_up = factory.LazyFunction(lambda: [ExerciseSequence()])
    main_session = factory.LazyFunction(lambda: [ExerciseSequence()])
    cool_down = factory.LazyFunction(lambda: [ExerciseSequence()])

    @classmethod
    def create_in_repo(
        cls, repo: lesson_planning.Repository, **kwargs: object
    ) -> lesson_planning.LessonPlan:
        lesson_plan = cls.create(**kwargs)
        lesson_plan_id = repo.create_lesson_plan(
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
        model = generate_lesson_plan.LessonPlanRequirements

    duration_minutes = 30
    target_difficulty = lesson_planning.Difficulty.INTERMEDIATE
    target_muscle_groups = factory.LazyFunction(
        lambda: [lesson_planning.MuscleGroup.CORE]
    )
    example_lesson_lan_ids = factory.ListFactory()
    user_prompt = factory.Sequence(lambda n: f"use-prompt-{n}")
