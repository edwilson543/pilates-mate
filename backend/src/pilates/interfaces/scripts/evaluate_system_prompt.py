import argparse
import asyncio

from pilates import config
from pilates.domain import exercises, lesson_plans


async def evaluate_prompt(*, version: str = "v1") -> str:
    requirements_list = _get_evaluation_requirements()
    uow = config.get_unit_of_work()

    evaluation_tasks = [
        _generate_and_evaluate(
            lesson_plans.get_system_prompt(
                requirements, uow.lesson_plans, uow.exercises, version=version
            ),
            requirements,
        )
        for requirements in requirements_list
    ]
    evaluations = await asyncio.gather(*evaluation_tasks)

    aggregated = lesson_plans.GeneratedLessonPlanEvaluation.aggregate(evaluations)
    return aggregated.render()


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
    full_body = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=45,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=available_equipment,
            user_prompt="Focus on core and glutes equally, but weave in some focus on the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
        for available_equipment in [[], [exercises.Equipment.BALL]]
    ]
    core_focus = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=30,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=[exercises.Equipment.BALL],
            user_prompt="Focus mainly on core today, with equal balance given to the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
    ]
    glutes_focus = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=30,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=[exercises.Equipment.BALL],
            user_prompt="Focus mainly on a glutes blast, with equal balance given to the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
    ]
    return full_body + core_focus + glutes_focus


def _main():
    parser = argparse.ArgumentParser(
        description="Evaluate system prompt template across multiple test scenarios."
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="Template version to evaluate (default: v1)",
    )
    args = parser.parse_args()

    print(f"Evaluating template version: {args.version}")
    print()

    result = asyncio.run(evaluate_prompt(version=args.version))
    print(result)


if __name__ == "__main__":
    _main()
