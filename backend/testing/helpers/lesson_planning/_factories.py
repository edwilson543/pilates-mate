import datetime as dt

import factory

from pilates.domain import lesson_planning


class Exercise(factory.Factory):
    class Meta:
        model = lesson_planning.Exercise

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    difficulty = lesson_planning.Difficulty.INTERMEDIATE
    primary_muscle_group = lesson_planning.MuscleGroup.CORE
    starting_position = lesson_planning.StartingPosition.STANDING


class ExerciseSet(factory.Factory):
    class Meta:
        model = lesson_planning.ExerciseSet

    exercise = factory.SubFactory(Exercise)
    reps = 10
    duration_seconds = 30


class ExerciseSequence(factory.Factory):
    class Meta:
        model = lesson_planning.ExerciseSequence
        exclude = ("n_sets",)

    sets = factory.LazyAttribute(lambda o: [ExerciseSet() for _ in range(o.n_sets)])
    name = factory.Sequence(lambda n: f"name-{n}")
    notes = factory.Sequence(lambda n: f"notes-{n}")
    n_sets = 3


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
