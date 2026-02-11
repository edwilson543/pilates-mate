import abc

from . import _models


class Repository(abc.ABC):
    # Exercises.

    @abc.abstractmethod
    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        difficulty: _models.Difficulty,
        primary_muscle_group: _models.MuscleGroup,
        starting_position: _models.StartingPosition,
    ) -> list[_models.Exercise]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercises(self) -> list[_models.Exercise]:
        raise NotImplementedError

    # Lesson plans.

    @abc.abstractmethod
    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        warm_up: list[_models.ExerciseSequence],
        main_session: list[_models.ExerciseSequence],
        cool_down: list[_models.ExerciseSequence],
    ) -> list[_models.LessonPlan]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_lesson_plans(self) -> list[_models.LessonPlan]:
        raise NotImplementedError
