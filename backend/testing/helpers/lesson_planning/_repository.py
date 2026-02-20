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
        variants: list[lesson_planning.ExerciseVariant],
    ) -> int:
        next_id = len(self._exercises) + 1

        new_exercise = lesson_planning.Exercise(
            id=next_id,
            name=name,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            variants=variants,
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

    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        description: str,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
        variants: list[lesson_planning.ExerciseVariant],
    ) -> None:
        # Find exercise index
        exercise_index = None
        for idx, exercise in enumerate(self._exercises):
            if exercise.id == id:
                exercise_index = idx
                break

        if exercise_index is None:
            raise lesson_planning.ExerciseDoesNotExist(exercise_id=id)

        # Create updated exercise
        updated_exercise = lesson_planning.Exercise(
            id=id,
            name=name,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            variants=variants,
        )

        # Update in exercises list
        updated_exercises = self._exercises.copy()
        updated_exercises[exercise_index] = updated_exercise
        object.__setattr__(self, "_exercises", updated_exercises)

        # Update all references in lesson plans (denormalization handling)
        updated_lesson_plans = []
        for plan in self._lesson_plans:
            updated_warm_up = self._update_sequences(plan.warm_up, id, updated_exercise)
            updated_main_session = self._update_sequences(
                plan.main_session, id, updated_exercise
            )
            updated_cool_down = self._update_sequences(
                plan.cool_down, id, updated_exercise
            )

            updated_plan = plan.model_copy(
                update={
                    "warm_up": updated_warm_up,
                    "main_session": updated_main_session,
                    "cool_down": updated_cool_down,
                }
            )
            updated_lesson_plans.append(updated_plan)

        object.__setattr__(self, "_lesson_plans", updated_lesson_plans)

    def _update_sequences(
        self,
        sequences: list[lesson_planning.ExerciseSequence],
        exercise_id: int,
        updated_exercise: lesson_planning.Exercise,
    ) -> list[lesson_planning.ExerciseSequence]:
        """Update exercise references in a list of sequences."""
        updated_sequences = []
        for sequence in sequences:
            updated_sets = []
            for exercise_set in sequence.sets:
                if exercise_set.exercise.id == exercise_id:
                    updated_set = exercise_set.model_copy(
                        update={"exercise": updated_exercise}
                    )
                    updated_sets.append(updated_set)
                else:
                    updated_sets.append(exercise_set)

            updated_sequence = sequence.model_copy(update={"sets": updated_sets})
            updated_sequences.append(updated_sequence)

        return updated_sequences

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

    def delete_lesson_plan(self, lesson_plan_id: int) -> None:
        plan_exists = any(plan.id == lesson_plan_id for plan in self._lesson_plans)
        if not plan_exists:
            raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        filtered_plans = [
            plan for plan in self._lesson_plans if plan.id != lesson_plan_id
        ]
        object.__setattr__(self, "_lesson_plans", filtered_plans)
