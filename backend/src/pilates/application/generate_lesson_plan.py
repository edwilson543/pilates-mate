import attrs

from pilates.domain import lesson_plans, unit_of_work, vendors


LessonPlanDoesNotExist = lesson_plans.LessonPlanDoesNotExist
UnableToGenerateLessonPlan = lesson_plans.UnableToGenerateLessonPlan


@attrs.frozen
class LessonPlanNotPendingGeneration(Exception):
    status: lesson_plans.LessonPlanStatus


async def generate_lesson_plan(
    *,
    lesson_plan_id: int,
    client: vendors.CompletionClient,
    uow: unit_of_work.UnitOfWork,
) -> None:
    """
    Generate a lesson plan that is currently initiated.

    :raises LessonPlanDoesNotExist: If no lesson plan with the given ID exists.
    :raises LessonPlanNotPendingGeneration: If the lesson plan is not pending generation.
    :raises UnableToGenerateLessonPlan: If the generation fails for some reason.
    """
    lesson_plan = uow.lesson_plans.get_lesson_plan(lesson_plan_id=lesson_plan_id)
    if lesson_plan.status != lesson_plans.LessonPlanStatus.PENDING_GENERATION:
        raise LessonPlanNotPendingGeneration(status=lesson_plan.status)

    system_prompt = lesson_plans.get_system_prompt(
        requirements=lesson_plan.requirements,
        lesson_plans_repo=uow.lesson_plans,
        exercises_repo=uow.exercises,
    )

    try:
        generated_plan = await lesson_plans.generate_lesson_plan(
            requirements=lesson_plan.requirements,
            client=client,
            system_prompt=system_prompt,
        )
    except lesson_plans.UnableToGenerateLessonPlan:
        uow.lesson_plans.update_lesson_plan(
            lesson_plan_id,
            name=lesson_plan.name,
            description="Errored during generation.",
            status=lesson_plans.LessonPlanStatus.ERRORED,
        )
        raise

    await _persist_generated_lesson_plan(
        uow=uow, lesson_plan_id=lesson_plan_id, generated_plan=generated_plan
    )


async def _persist_generated_lesson_plan(
    *,
    uow: unit_of_work.UnitOfWork,
    lesson_plan_id: int,
    generated_plan: lesson_plans.GeneratedLessonPlan,
) -> None:
    async with uow.transaction():
        for sequence in generated_plan.warm_up:
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

        for sequence in generated_plan.main_session:
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

        for sequence in generated_plan.cool_down:
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

        uow.lesson_plans.update_lesson_plan(
            lesson_plan_id,
            name=generated_plan.name,
            description=generated_plan.description,
            status=lesson_plans.LessonPlanStatus.GENERATED,
        )
