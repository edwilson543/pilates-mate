import datetime as dt
import json
import pathlib

import attrs

from pilates.domain import lesson_planning


@attrs.frozen
class JSONRepository(lesson_planning.Repository):
    database_file: pathlib.Path = pathlib.Path(__file__).parent / "database.json"

    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
    ) -> int:
        data = self._read_database()

        next_id = max((exercise["id"] for exercise in data["exercises"]), default=0) + 1
        new_exercise = lesson_planning.Exercise(
            id=next_id,
            name=name,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
        )
        data["exercises"].append(new_exercise.model_dump())

        self._write_database(data)
        return next_id

    def get_exercises(self) -> list[lesson_planning.Exercise]:
        data = self._read_database()
        return [
            lesson_planning.Exercise.model_validate(exercise)
            for exercise in data["exercises"]
        ]

    def get_exercise(self, exercise_id: int) -> lesson_planning.Exercise:
        for exercise in self.get_exercises():
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
        data = self._read_database()

        next_id = max((plan["id"] for plan in data["lesson_plans"]), default=0) + 1

        new_lesson_plan = lesson_planning.LessonPlan(
            id=next_id,
            name=name,
            description=description,
            date=date,
            warm_up=warm_up,
            main_session=main_session,
            cool_down=cool_down,
        )
        data["lesson_plans"].append(new_lesson_plan.model_dump(mode="json"))

        self._write_database(data)

        return next_id

    def get_lesson_plans(self) -> list[lesson_planning.LessonPlan]:
        data = self._read_database()
        return [
            lesson_planning.LessonPlan.model_validate(plan)
            for plan in data["lesson_plans"]
        ]

    def get_lesson_plan(self, lesson_plan_id: int) -> lesson_planning.LessonPlan:
        for plan in self.get_lesson_plans():
            if plan.id == lesson_plan_id:
                return plan
        raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

    # Helpers.

    def _read_database(self) -> dict:
        self._maybe_init_database()
        with open(self.database_file, "r") as f:
            return json.load(f)

    def _write_database(self, data: dict) -> None:
        with open(self.database_file, "w") as f:
            json.dump(data, f, indent=2)

    def _maybe_init_database(self) -> None:
        if self.database_file.is_file():
            return None

        data: dict[str, list] = {
            "lesson_plans": [],
            "exercises": [],
        }

        with open(self.database_file, "x") as f:
            json.dump(data, f)
