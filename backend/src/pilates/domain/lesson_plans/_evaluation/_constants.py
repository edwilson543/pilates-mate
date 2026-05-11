from pilates.domain import exercises

from .. import _models


def get_evaluation_requirements() -> list[_models.LessonPlanRequirements]:
    """
    Get the lesson plan requirements to use when evaluating generated plans.
    """
    full_body = [
        _models.LessonPlanRequirements(
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
        _models.LessonPlanRequirements(
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
        _models.LessonPlanRequirements(
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
