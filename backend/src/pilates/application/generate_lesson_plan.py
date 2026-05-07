from pilates.domain import lesson_plans, unit_of_work, utils, vendors


UnableToGenerateLessonPlan = lesson_plans.UnableToGenerateLessonPlan


async def generate_lesson_plan(
    *,
    requirements: lesson_plans.LessonPlanRequirements,
    client: vendors.CompletionClient,
    uow: unit_of_work.UnitOfWork,
) -> lesson_plans.LessonPlan:
    system_prompt = lesson_plans.get_system_prompt(
        requirements=requirements,
        lesson_plans_repo=uow.lesson_plans,
        exercises_repo=uow.exercises,
    )

    lesson_plan = await lesson_plans.generate_lesson_plan(
        requirements=requirements, client=client, system_prompt=system_prompt
    )

    async with uow.transaction():
        # Initially, create an empty lesson plan.
        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name=lesson_plan.name,
            description=lesson_plan.description,
            date=utils.now().date(),
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
