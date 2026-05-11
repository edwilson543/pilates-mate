import datetime as dt

from pilates.domain import lesson_plans, unit_of_work


async def create_empty_lesson_plan_with_requirements(
    *,
    created_at: dt.date,
    requirements: lesson_plans.LessonPlanRequirements,
    uow: unit_of_work.UnitOfWork,
) -> int:
    name = f"{requirements.duration_minutes} minute blast - {created_at.strftime('%-d %B %Y')}"
    async with uow.transaction():
        return uow.lesson_plans.create_lesson_plan(
            name=name,
            date=created_at,
            requirements=requirements,
        )
