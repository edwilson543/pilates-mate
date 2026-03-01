import datetime as dt

import pydantic

from pilates.domain import exercises, lesson_plans, unit_of_work, vendors


class _GeneratedExercise(pydantic.BaseModel):
    id: int
    # Name is just included since LLMs are autoregressive.
    name: str


class _GeneratedExerciseSet(pydantic.BaseModel):
    exercise: _GeneratedExercise
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    equipment_variant: list[exercises.Equipment]


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



async def generate_lesson_plan(
    *,
    requirements: lesson_plans.LessonPlanRequirements,
    client: vendors.CompletionClient,
    uow: unit_of_work.UnitOfWork,
) -> lesson_plans.LessonPlan:
    system_prompt = _get_system_prompt(requirements, uow)

    lesson_plan = await client.get_completion(
        system_prompt=system_prompt,
        user_prompt=requirements.user_prompt,
        output_format=_GeneratedLessonPlan,
    )

    async with uow.transaction():
        # Initially, create an empty lesson plan.
        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name=lesson_plan.name,
            description=lesson_plan.description,
            date=dt.datetime.now().date(),
            warm_up=[],
            main_session=[],
            cool_down=[],
        )

        # Add warm up sequences and sets
        for sequence in lesson_plan.warm_up:
            sequence_id = uow.lesson_plans.add_sequence_to_section(
                lesson_plan_id=lesson_plan_id,
                section=lesson_plans.LessonPlanSection.WARM_UP,
                name=sequence.name,
                reps=sequence.reps,
                notes=sequence.notes,
            )
            for set_item in sequence.sets:
                uow.lesson_plans.add_set_to_sequence(
                    sequence_id=sequence_id,
                    exercise_id=set_item.exercise.id,
                    reps=set_item.reps,
                    duration_seconds=set_item.duration_seconds,
                    movement_variant=set_item.movement_variant,
                    equipment_variant=set_item.equipment_variant,
                )

        # Add main session sequences and sets
        for sequence in lesson_plan.main_session:
            sequence_id = uow.lesson_plans.add_sequence_to_section(
                lesson_plan_id=lesson_plan_id,
                section=lesson_plans.LessonPlanSection.MAIN_SESSION,
                name=sequence.name,
                reps=sequence.reps,
                notes=sequence.notes,
            )
            for set_item in sequence.sets:
                uow.lesson_plans.add_set_to_sequence(
                    sequence_id=sequence_id,
                    exercise_id=set_item.exercise.id,
                    reps=set_item.reps,
                    duration_seconds=set_item.duration_seconds,
                    movement_variant=set_item.movement_variant,
                    equipment_variant=set_item.equipment_variant,
                )

        # Add cool down sequences and sets
        for sequence in lesson_plan.cool_down:
            sequence_id = uow.lesson_plans.add_sequence_to_section(
                lesson_plan_id=lesson_plan_id,
                section=lesson_plans.LessonPlanSection.COOL_DOWN,
                name=sequence.name,
                reps=sequence.reps,
                notes=sequence.notes,
            )
            for set_item in sequence.sets:
                uow.lesson_plans.add_set_to_sequence(
                    sequence_id=sequence_id,
                    exercise_id=set_item.exercise.id,
                    reps=set_item.reps,
                    duration_seconds=set_item.duration_seconds,
                    movement_variant=set_item.movement_variant,
                    equipment_variant=set_item.equipment_variant,
                )

    return uow.lesson_plans.get_lesson_plan(lesson_plan_id)


def _get_system_prompt(
    requirements: lesson_plans.LessonPlanRequirements,
    uow: unit_of_work.UnitOfWork,
) -> str:
    all_exercises = uow.exercises.get_exercises()
    example_lesson_plans = _get_example_lesson_plans(requirements, uow.lesson_plans)

    return lesson_plans.render_system_prompt(
        duration_minutes=requirements.duration_minutes,
        target_difficulty=requirements.target_difficulty,
        target_muscle_groups=requirements.target_muscle_groups,
        available_equipment=requirements.available_equipment,
        all_exercises=all_exercises,
        example_lesson_plans=example_lesson_plans,
    )


def _get_example_lesson_plans(
    requirements: lesson_plans.LessonPlanRequirements,
    repository: lesson_plans.Repository,
) -> list[lesson_plans.LessonPlan]:
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
