import json
import pathlib

from pilates.domain import lesson_planning
from pilates.domain.lesson_planning import _models


class JSONRepository(lesson_planning.Repository):
    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
    ) -> list[lesson_planning.Exercise]:
        self._init_database()
        # TODO

    def get_exercises(self) -> list[lesson_planning.Exercise]:
        # TODO
        pass

    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        warm_up: list[lesson_planning.ExerciseSequence],
        main_session: list[lesson_planning.ExerciseSequence],
        cool_down: list[lesson_planning.ExerciseSequence],
    ) -> list[lesson_planning.LessonPlan]:
        self._init_database()
        # TODO

    def get_lesson_plans(self) -> list[_models.LessonPlan]:
        # TODO
        pass

    # Helpers.

    def _init_database(self) -> None:
        if self.database_file.is_file():
            return None

        data = {
            "lesson_plans": [],
            "exercises": [],
        }

        with open(self.database_file, "x") as f:
            json.dump(data, f)

    @property
    def database_file(self) -> pathlib.Path:
        return pathlib.Path(__file__).parent / "database.json"
