import factory

from pilates.domain import exercises, lesson_plans, unit_of_work


class Exercise(factory.Factory):
    class Meta:
        model = exercises.Exercise

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    category = exercises.ExerciseCategory.EFFORT
    difficulty = exercises.Difficulty.INTERMEDIATE
    primary_muscle_group = exercises.MuscleGroup.CORE
    starting_position = exercises.StartingPosition.STANDING
    movement_variants = factory.LazyFunction(
        lambda: [exercises.MovementVariant.STANDARD]
    )
    equipment_variants = factory.LazyFunction(lambda: [exercises.Equipment.BALL])

    @classmethod
    def insert(
        cls, uow: unit_of_work.UnitOfWork, **kwargs: object
    ) -> lesson_plans.LessonPlan:
        exercise = cls.create(**kwargs)
        exercise_id = uow.exercises.create_exercise(
            name=exercise.name,
            description=exercise.description,
            category=exercise.category,
            difficulty=exercise.difficulty,
            primary_muscle_group=exercise.primary_muscle_group,
            starting_position=exercise.starting_position,
            movement_variants=exercise.movement_variants,
            equipment_variants=exercise.equipment_variants,
        )
        exercise.id = exercise_id
        return exercise
