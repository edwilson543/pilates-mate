import asyncio

from pilates import config
from pilates.domain import exercises, lesson_plans


async def _evaluate_prompt(
    system_prompt: str,
) -> lesson_plans.GeneratedLessonPlanEvaluation:
    requirements_list = _get_evaluation_requirements()

    evaluation_tasks = [
        _generate_and_evaluate(system_prompt, requirements)
        for requirements in requirements_list
    ]
    evaluations = await asyncio.gather(*evaluation_tasks)

    return lesson_plans.GeneratedLessonPlanEvaluation.calculate_mean(evaluations)


async def _generate_and_evaluate(
    system_prompt: str, requirements: lesson_plans.LessonPlanRequirements
) -> lesson_plans.GeneratedLessonPlanEvaluation:
    completion_client = config.get_completion_client()
    deps = config.get_evaluation_deps()

    generated_plan = await lesson_plans.generate_lesson_plan(
        requirements=requirements,
        client=completion_client,
        system_prompt=system_prompt,
    )

    return lesson_plans.evaluate_generated_lesson_plan(
        generated_plan=generated_plan, requirements=requirements, deps=deps
    )


def _get_evaluation_requirements() -> list[lesson_plans.LessonPlanRequirements]:
    return [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=45,
            target_difficulty=exercises.Difficulty.INTERMEDIATE,
            target_muscle_groups=[
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.CORE,
            ],
            example_lesson_plan_ids=[],
            available_equipment=[exercises.Equipment.BALL],
            user_prompt="",
        )
    ]
