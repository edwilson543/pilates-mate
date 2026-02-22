import datetime as dt
import pathlib

import pytest

from pilates.data.json_repositories import _lesson_planning
from pilates.domain import lesson_planning
from testing.helpers import lesson_planning as lesson_planning_helpers


class TestCreateExercise:
    def test_creates_exercise_with_given_parameters(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_exercise(
            name="Hundred",
            description="Classic Pilates breathing exercise",
            category=lesson_planning.ExerciseCategory.BREATH_WORK,
            difficulty=lesson_planning.Difficulty.BEGINNER,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.SUPINE,
            movement_variants=[lesson_planning.MovementVariant.STANDARD],
            equipment_variants=[],
        )

        assert lesson_plan_id == 1


class TestGetExercises:
    def test_returns_all_created_exercises(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_planning_helpers.Exercise.create_in_repo(repository, name="Hundred")
        lesson_planning_helpers.Exercise.create_in_repo(repository, name="Roll Up")

        exercises = repository.get_exercises()

        assert len(exercises) == 2
        assert exercises[0].name == "Hundred"
        assert exercises[1].name == "Roll Up"


class TestGetExercise:
    def test_returns_exercise_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise = lesson_planning_helpers.Exercise.create_in_repo(
            repository, name="Plank", description="Core stability exercise"
        )

        result = repository.get_exercise(exercise.id)

        assert result.id == exercise.id
        assert result.name == "Plank"
        assert result.description == "Core stability exercise"

    def test_raises_exception_when_exercise_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.ExerciseDoesNotExist) as exc_info:
            repository.get_exercise(999)

        assert exc_info.value.exercise_id == 999


class TestCreateLessonPlan:
    def test_returns_lesson_plan_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            date=dt.date(2026, 1, 15),
            warm_up=[],
            main_session=[],
            cool_down=[],
        )

        assert lesson_plan_id == 1

    def test_creates_lesson_plan_with_empty_sections(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            date=dt.date(2026, 1, 15),
            warm_up=[],
            main_session=[],
            cool_down=[],
        )

        lesson_plan = repository.get_lesson_plan(lesson_plan_id)
        assert lesson_plan.warm_up == []
        assert lesson_plan.main_session == []
        assert lesson_plan.cool_down == []


class TestGetLessonPlans:
    def test_returns_all_created_lesson_plans(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, name="Beginner Flow"
        )
        lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, name="Advanced Flow"
        )

        lesson_plans = repository.get_lesson_plans()

        assert len(lesson_plans) == 2
        assert lesson_plans[0].name == "Beginner Flow"
        assert lesson_plans[1].name == "Advanced Flow"


class TestGetLessonPlan:
    def test_returns_lesson_plan_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository,
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
        )

        result = repository.get_lesson_plan(lesson_plan.id)

        assert result.id == lesson_plan.id
        assert result.name == "Beginner Flow"
        assert result.description == "A gentle introduction to Pilates"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.LessonPlanDoesNotExist) as exc_info:
            repository.get_lesson_plan(999)

        assert exc_info.value.lesson_plan_id == 999


class TestDeleteLessonPlan:
    def test_deletes_lesson_plan_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_plan_1 = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, name="Beginner Flow"
        )
        lesson_plan_2 = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, name="Advanced Flow"
        )

        repository.delete_lesson_plan(lesson_plan_1.id)

        remaining_plans = repository.get_lesson_plans()
        assert len(remaining_plans) == 1
        assert remaining_plans[0].id == lesson_plan_2.id
        assert remaining_plans[0].name == "Advanced Flow"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.LessonPlanDoesNotExist) as exc_info:
            repository.delete_lesson_plan(999)

        assert exc_info.value.lesson_plan_id == 999


class TestAddSequenceToSection:
    def test_adds_sequence_to_warm_up_section(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_planning.LessonPlanSection.WARM_UP,
            name="Breathing Sequence",
            reps=1,
            notes="Focus on deep breaths",
        )

        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up) == 1
        assert plan.warm_up[0].id == sequence_id
        assert plan.warm_up[0].name == "Breathing Sequence"
        assert plan.warm_up[0].reps == 1
        assert plan.warm_up[0].notes == "Focus on deep breaths"
        assert plan.warm_up[0].sets == []

    def test_adds_sequence_to_main_session_section(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_planning.LessonPlanSection.MAIN_SESSION,
            name="Core Work",
            reps=3,
            notes="Maintain form",
        )

        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.main_session) == 1
        assert plan.main_session[0].id == sequence_id

    def test_adds_multiple_sequences_to_same_section(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id_1 = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_planning.LessonPlanSection.WARM_UP,
            name="First Sequence",
            reps=1,
            notes="Notes 1",
        )
        sequence_id_2 = repository.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_planning.LessonPlanSection.WARM_UP,
            name="Second Sequence",
            reps=2,
            notes="Notes 2",
        )

        assert sequence_id_2 == sequence_id_1 + 1
        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up) == 2
        assert plan.warm_up[0].name == "First Sequence"
        assert plan.warm_up[1].name == "Second Sequence"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.LessonPlanDoesNotExist) as exc_info:
            repository.add_sequence_to_section(
                lesson_plan_id=999,
                section=lesson_planning.LessonPlanSection.WARM_UP,
                name="Test Sequence",
                reps=1,
                notes="Test notes",
            )

        assert exc_info.value.lesson_plan_id == 999


class TestAddSetToSequence:
    def test_adds_set_to_sequence(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence], main_session=[], cool_down=[]
        )

        sequence_id = lesson_plan.warm_up[0].id

        set_id = repository.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=5,
            duration_seconds=30,
            movement_variant=lesson_planning.MovementVariant.STANDARD,
            equipment_variant=[],
        )

        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 1
        assert plan.warm_up[0].sets[0].id == set_id
        assert plan.warm_up[0].sets[0].exercise.id == exercise.id
        assert plan.warm_up[0].sets[0].reps == 5
        assert plan.warm_up[0].sets[0].duration_seconds == 30
        assert (
            plan.warm_up[0].sets[0].movement_variant
            == lesson_planning.MovementVariant.STANDARD
        )

    def test_adds_multiple_sets_to_same_sequence(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence]
        )

        sequence_id = lesson_plan.warm_up[0].id

        set_id_1 = repository.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=5,
            duration_seconds=30,
            movement_variant=lesson_planning.MovementVariant.STANDARD,
            equipment_variant=[],
        )
        set_id_2 = repository.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=10,
            duration_seconds=60,
            movement_variant=lesson_planning.MovementVariant.PULSE,
            equipment_variant=[],
        )

        assert set_id_2 == set_id_1 + 1
        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 2
        assert plan.warm_up[0].sets[0].reps == 5
        assert plan.warm_up[0].sets[1].reps == 10

    def test_raises_exception_when_sequence_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)

        with pytest.raises(lesson_planning.SequenceDoesNotExist) as exc_info:
            repository.add_set_to_sequence(
                sequence_id=999,
                exercise_id=exercise.id,
                reps=5,
                duration_seconds=30,
                movement_variant=lesson_planning.MovementVariant.STANDARD,
                equipment_variant=[],
            )

        assert exc_info.value.sequence_id == 999

    def test_raises_exception_when_exercise_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence]
        )

        sequence_id = lesson_plan.warm_up[0].id

        with pytest.raises(lesson_planning.ExerciseDoesNotExist) as exc_info:
            repository.add_set_to_sequence(
                sequence_id=sequence_id,
                exercise_id=999,
                reps=5,
                duration_seconds=30,
                movement_variant=lesson_planning.MovementVariant.STANDARD,
                equipment_variant=[],
            )

        assert exc_info.value.exercise_id == 999


class TestGetExerciseSet:
    def test_returns_set_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise_set = lesson_planning_helpers.ExerciseSet(reps=5, duration_seconds=30)
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[exercise_set])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence]
        )

        set_id = lesson_plan.warm_up[0].sets[0].id

        result = repository.get_exercise_set(set_id)

        assert result.id == set_id
        assert result.reps == 5
        assert result.duration_seconds == 30
        assert result.movement_variant == exercise_set.movement_variant

    def test_raises_exception_when_set_does_not_exist(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.SetDoesNotExist) as exc_info:
            repository.get_exercise_set(999)

        assert exc_info.value.set_id == 999


class TestUpdateExerciseSet:
    def test_updates_set_properties(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise_set = lesson_planning_helpers.ExerciseSet(
            reps=5, duration_seconds=30, movement_variant="STANDARD"
        )
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[exercise_set])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence]
        )

        set_id = lesson_plan.warm_up[0].sets[0].id

        repository.update_exercise_set(
            id=set_id,
            reps=10,
            duration_seconds=60,
            movement_variant=lesson_planning.MovementVariant.PULSE,
            equipment_variant=[],
        )

        updated_set = repository.get_exercise_set(set_id)
        assert updated_set.reps == 10
        assert updated_set.duration_seconds == 60
        assert updated_set.movement_variant == lesson_planning.MovementVariant.PULSE

    def test_raises_exception_when_set_does_not_exist(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.SetDoesNotExist) as exc_info:
            repository.update_exercise_set(
                id=999,
                reps=10,
                duration_seconds=60,
                movement_variant=lesson_planning.MovementVariant.PULSE,
                equipment_variant=[],
            )

        assert exc_info.value.set_id == 999


class TestDeleteExerciseSet:
    def test_deletes_set_from_sequence(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        set_1 = lesson_planning_helpers.ExerciseSet()
        set_2 = lesson_planning_helpers.ExerciseSet()
        sequence = lesson_planning_helpers.ExerciseSequence(sets=[set_1, set_2])
        lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
            repository, warm_up=[sequence]
        )

        set_1_id = lesson_plan.warm_up[0].sets[0].id
        set_2_id = lesson_plan.warm_up[0].sets[1].id

        repository.delete_exercise_set(set_1_id)

        plan = repository.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 1
        assert plan.warm_up[0].sets[0].id == set_2_id

    def test_raises_exception_when_set_does_not_exist(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.SetDoesNotExist) as exc_info:
            repository.delete_exercise_set(999)

        assert exc_info.value.set_id == 999


def test_database_isnt_corrupted():
    repository = _lesson_planning.JSONRepository()

    assert repository.get_exercises() is not None
    assert repository.get_lesson_plans() is not None
