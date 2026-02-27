from pilates.domain import exercises
from pilates.domain.lesson_plans import _generation
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers


class TestRenderSystemPrompt:
    def test_renders_without_smoke(self):
        warm_up_exercise = exercise_helpers.Exercise()
        main_exercise = exercise_helpers.Exercise()
        cool_down_exercise = exercise_helpers.Exercise()

        warm_up_set = lesson_plan_helpers.ExerciseSet(exercise_id=warm_up_exercise.id)
        main_set = lesson_plan_helpers.ExerciseSet(exercise_id=main_exercise.id)
        cool_down_set = lesson_plan_helpers.ExerciseSet(
            exercise_id=cool_down_exercise.id
        )

        warm_up = lesson_plan_helpers.ExerciseSequence(sets=[warm_up_set])
        main_session = lesson_plan_helpers.ExerciseSequence(sets=[main_set])
        cool_down = lesson_plan_helpers.ExerciseSequence(sets=[cool_down_set])

        lesson_plan = lesson_plan_helpers.LessonPlan(
            warm_up=[warm_up], main_session=[main_session], cool_down=[cool_down]
        )

        system_prompt = _generation.render_system_prompt(
            duration_minutes=30,
            target_difficulty=exercises.Difficulty.INTERMEDIATE,
            target_muscle_groups=[exercises.MuscleGroup.GLUTES],
            available_equipment=[exercises.Equipment.BALL],
            all_exercises=[warm_up_exercise, main_exercise, cool_down_exercise],
            example_lesson_plans=[lesson_plan],
        )

        assert system_prompt is not None
