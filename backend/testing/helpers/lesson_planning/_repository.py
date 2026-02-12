import datetime as dt

import attrs

from pilates.domain import lesson_planning


@attrs.frozen
class FakeRepository(lesson_planning.Repository):
    _exercises: list[lesson_planning.Exercise] = attrs.field(factory=list)
    _lesson_plans: list[lesson_planning.LessonPlan] = attrs.field(factory=list)

    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
    ) -> int:
        next_id = len(self._exercises) + 1

        new_exercise = lesson_planning.Exercise(
            id=next_id,
            name=name,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
        )
        self._exercises.append(new_exercise)

        return next_id

    def get_exercises(self) -> list[lesson_planning.Exercise]:
        return self._exercises.copy()

    def get_exercise(self, exercise_id: int) -> lesson_planning.Exercise:
        for exercise in self._exercises:
            if exercise.id == exercise_id:
                return exercise
        raise lesson_planning.ExerciseDoesNotExist(exercise_id=exercise_id)

    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        date: dt.date,
        warm_up: list[lesson_planning.ExerciseSequence],
        main_session: list[lesson_planning.ExerciseSequence],
        cool_down: list[lesson_planning.ExerciseSequence],
    ) -> int:
        next_id = len(self._lesson_plans) + 1

        new_lesson_plan = lesson_planning.LessonPlan(
            id=next_id,
            name=name,
            description=description,
            date=date,
            warm_up=warm_up,
            main_session=main_session,
            cool_down=cool_down,
        )
        self._lesson_plans.append(new_lesson_plan)

        return next_id

    def get_lesson_plans(self) -> list[lesson_planning.LessonPlan]:
        return self._lesson_plans.copy()

    def get_lesson_plan(self, lesson_plan_id: int) -> lesson_planning.LessonPlan:
        for plan in self._lesson_plans:
            if plan.id == lesson_plan_id:
                return plan
        raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)
