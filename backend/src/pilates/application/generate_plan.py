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

    # Create empty lesson plan
    lesson_plan_id = repository.create_lesson_plan(
        name=lesson_plan.name,
        description=lesson_plan.description,
        date=dt.datetime.now().date(),
    )

    # Add warm up sequences and sets
    for sequence in lesson_plan.warm_up:
        sequence_id = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan_id,
            section=lesson_planning.LessonPlanSection.WARM_UP,
            name=sequence.name,
            reps=sequence.reps,
            notes=sequence.notes,
        )
        for set_item in sequence.sets:
            repository.add_set_to_sequence(
                sequence_id=sequence_id,
                exercise_id=set_item.exercise.id,
                reps=set_item.reps,
                duration_seconds=set_item.duration_seconds,
                variant=set_item.variant,
            )

    # Add main session sequences and sets
    for sequence in lesson_plan.main_session:
        sequence_id = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan_id,
            section=lesson_planning.LessonPlanSection.MAIN_SESSION,
            name=sequence.name,
            reps=sequence.reps,
            notes=sequence.notes,
        )
        for set_item in sequence.sets:
            repository.add_set_to_sequence(
                sequence_id=sequence_id,
                exercise_id=set_item.exercise.id,
                reps=set_item.reps,
                duration_seconds=set_item.duration_seconds,
                variant=set_item.variant,
            )

    # Add cool down sequences and sets
    for sequence in lesson_plan.cool_down:
        sequence_id = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan_id,
            section=lesson_planning.LessonPlanSection.COOL_DOWN,
            name=sequence.name,
            reps=sequence.reps,
            notes=sequence.notes,
        )
        for set_item in sequence.sets:
            repository.add_set_to_sequence(
                sequence_id=sequence_id,
                exercise_id=set_item.exercise.id,
                reps=set_item.reps,
                duration_seconds=set_item.duration_seconds,
                variant=set_item.variant,
            )

    return repository.get_lesson_plan(lesson_plan_id)


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
