import datetime as dt

import pydantic

from pilates.domain import lesson_planning, vendors


class _GeneratedExercise(pydantic.BaseModel):
    id: int
    # Name is just included since LLMs are autoregressive.
    name: str


class _GeneratedExerciseSet(pydantic.BaseModel):
    exercise: _GeneratedExercise
    reps: int
    duration_seconds: int
    variant: lesson_planning.ExerciseVariant


class _GeneratedExerciseSequence(pydantic.BaseModel):
    name: str
    sets: list[_GeneratedExerciseSet]
    reps: int
    notes: str


class _GeneratedLessonPlan(pydantic.BaseModel):
    name: str
    description: str
    warm_up: list[_GeneratedExerciseSequence]
    main_session: list[_GeneratedExerciseSequence]
    cool_down: list[_GeneratedExerciseSequence]


class LessonPlanRequirements(pydantic.BaseModel):
    duration_minutes: int
    target_difficulty: lesson_planning.Difficulty
    target_muscle_groups: list[lesson_planning.MuscleGroup]
    example_lesson_plan_ids: list[int] = []
    user_prompt: str


async def generate_lesson_plan(
    *,
    requirements: LessonPlanRequirements,
    client: vendors.CompletionClient,
    repository: lesson_planning.Repository,
) -> lesson_planning.LessonPlan:
    system_prompt = _get_system_prompt(requirements, repository)

    lesson_plan = await client.get_completion(
        system_prompt=system_prompt,
        user_prompt=requirements.user_prompt,
        output_format=_GeneratedLessonPlan,
    )

    # Transform AI-generated sequences (without IDs) to domain models (with IDs)
    warm_up = _transform_sequences(lesson_plan.warm_up, repository)
    main_session = _transform_sequences(lesson_plan.main_session, repository)
    cool_down = _transform_sequences(lesson_plan.cool_down, repository)

    lesson_plan_id = repository.create_lesson_plan(
        name=lesson_plan.name,
        description=lesson_plan.description,
        date=dt.datetime.now().date(),
        warm_up=warm_up,
        main_session=main_session,
        cool_down=cool_down,
    )

    return repository.get_lesson_plan(lesson_plan_id)


def _transform_sequences(
    generated_sequences: list[_GeneratedExerciseSequence],
    repository: lesson_planning.Repository,
) -> list[lesson_planning.ExerciseSequence]:
    """Transform AI-generated sequences (without IDs) to domain models (with IDs)."""
    sequences = []
    sequence_id = 1
    set_id = 1

    for generated_seq in generated_sequences:
        sets = []
        for generated_set in generated_seq.sets:
            # Fetch the full exercise object from repository
            exercise = repository.get_exercise(generated_set.exercise.id)

            exercise_set = lesson_planning.ExerciseSet(
                id=set_id,
                exercise=exercise,
                reps=generated_set.reps,
                duration_seconds=generated_set.duration_seconds,
                variant=generated_set.variant,
            )
            sets.append(exercise_set)
            set_id += 1

        sequence = lesson_planning.ExerciseSequence(
            id=sequence_id,
            name=generated_seq.name,
            sets=sets,
            reps=generated_seq.reps,
            notes=generated_seq.notes,
        )
        sequences.append(sequence)
        sequence_id += 1

    return sequences


def _get_system_prompt(
    requirements: LessonPlanRequirements,
    repository: lesson_planning.Repository,
) -> str:
    # TODO -> filter exercises by the available equipment.
    all_exercises = repository.get_exercises()
    example_lesson_plans = _get_example_lesson_plans(requirements, repository)

    return lesson_planning.render_system_prompt(
        duration_minutes=requirements.duration_minutes,
        target_difficulty=requirements.target_difficulty,
        target_muscle_groups=requirements.target_muscle_groups,
        all_exercises=all_exercises,
        example_lesson_plans=example_lesson_plans,
    )


def _get_example_lesson_plans(
    requirements: LessonPlanRequirements,
    repository: lesson_planning.Repository,
) -> list[lesson_planning.LessonPlan]:
    all_lesson_plans = repository.get_lesson_plans()
    if requirements.example_lesson_plan_ids:
        example_lesson_plans = [
            lesson_plan
            for lesson_plan in all_lesson_plans
            if lesson_plan in requirements.example_lesson_plan_ids
        ]
    else:
        # Fallback to using the three most recent plans.
        example_lesson_plans = sorted(all_lesson_plans, key=lambda lp: lp.date)[-3:]

    return example_lesson_plans
