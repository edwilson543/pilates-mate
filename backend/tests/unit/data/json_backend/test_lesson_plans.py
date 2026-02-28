import datetime as dt

import pytest

from pilates.data.json_backend import _unit_of_work
from pilates.domain import exercises, lesson_plans
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers


class TestCreateLessonPlan:
    def test_returns_lesson_plan_id(self, uow: _unit_of_work.JSONUnitOfWork):
        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            date=dt.date(2026, 1, 15),
            warm_up=[],
            main_session=[],
            cool_down=[],
        )

        assert lesson_plan_id == 1

    def test_creates_lesson_plan_with_empty_sections(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            date=dt.date(2026, 1, 15),
            warm_up=[],
            main_session=[],
            cool_down=[],
        )

        lesson_plan = uow.lesson_plans.get_lesson_plan(lesson_plan_id)
        assert lesson_plan.warm_up == []
        assert lesson_plan.main_session == []
        assert lesson_plan.cool_down == []


class TestGetLessonPlans:
    def test_returns_all_created_lesson_plans(self, uow: _unit_of_work.JSONUnitOfWork):
        lesson_plan_helpers.LessonPlan.insert(uow, name="Beginner Flow")
        lesson_plan_helpers.LessonPlan.insert(uow, name="Advanced Flow")

        lesson_plans = uow.lesson_plans.get_lesson_plans()

        assert len(lesson_plans) == 2
        assert lesson_plans[0].name == "Beginner Flow"
        assert lesson_plans[1].name == "Advanced Flow"


class TestGetLessonPlan:
    def test_returns_lesson_plan_with_matching_id(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow,
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
        )

        result = uow.lesson_plans.get_lesson_plan(lesson_plan.id)

        assert result.id == lesson_plan.id
        assert result.name == "Beginner Flow"
        assert result.description == "A gentle introduction to Pilates"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.LessonPlanDoesNotExist) as exc_info:
            uow.lesson_plans.get_lesson_plan(999)

        assert exc_info.value.lesson_plan_id == 999


class TestDeleteLessonPlan:
    def test_deletes_lesson_plan_with_matching_id(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan_1 = lesson_plan_helpers.LessonPlan.insert(uow, name="Beginner Flow")
        lesson_plan_2 = lesson_plan_helpers.LessonPlan.insert(uow, name="Advanced Flow")

        uow.lesson_plans.delete_lesson_plan(lesson_plan_1.id)

        remaining_plans = uow.lesson_plans.get_lesson_plans()
        assert len(remaining_plans) == 1
        assert remaining_plans[0].id == lesson_plan_2.id
        assert remaining_plans[0].name == "Advanced Flow"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.LessonPlanDoesNotExist) as exc_info:
            uow.lesson_plans.delete_lesson_plan(999)

        assert exc_info.value.lesson_plan_id == 999


class TestAddSequenceToSection:
    def test_adds_sequence_to_warm_up_section(self, uow: _unit_of_work.JSONUnitOfWork):
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id = uow.lesson_plans.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_plans.LessonPlanSection.WARM_UP,
            name="Breathing Sequence",
            reps=1,
            notes="Focus on deep breaths",
        )

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up) == 1
        assert plan.warm_up[0].id == sequence_id
        assert plan.warm_up[0].name == "Breathing Sequence"
        assert plan.warm_up[0].reps == 1
        assert plan.warm_up[0].notes == "Focus on deep breaths"
        assert plan.warm_up[0].sets == []

    def test_adds_sequence_to_main_session_section(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id = uow.lesson_plans.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_plans.LessonPlanSection.MAIN_SESSION,
            name="Core Work",
            reps=3,
            notes="Maintain form",
        )

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.main_session) == 1
        assert plan.main_session[0].id == sequence_id

    def test_adds_multiple_sequences_to_same_section(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, warm_up=[], main_session=[], cool_down=[]
        )

        sequence_id_1 = uow.lesson_plans.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_plans.LessonPlanSection.WARM_UP,
            name="First Sequence",
            reps=1,
            notes="Notes 1",
        )
        sequence_id_2 = uow.lesson_plans.add_sequence_to_section(
            lesson_plan_id=lesson_plan.id,
            section=lesson_plans.LessonPlanSection.WARM_UP,
            name="Second Sequence",
            reps=2,
            notes="Notes 2",
        )

        assert sequence_id_2 == sequence_id_1 + 1
        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up) == 2
        assert plan.warm_up[0].name == "First Sequence"
        assert plan.warm_up[1].name == "Second Sequence"

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.LessonPlanDoesNotExist) as exc_info:
            uow.lesson_plans.add_sequence_to_section(
                lesson_plan_id=999,
                section=lesson_plans.LessonPlanSection.WARM_UP,
                name="Test Sequence",
                reps=1,
                notes="Test notes",
            )

        assert exc_info.value.lesson_plan_id == 999


class TestAddSetToSequence:
    def test_adds_set_to_sequence(self, uow: _unit_of_work.JSONUnitOfWork):
        exercise = exercise_helpers.Exercise.insert(uow)
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, warm_up=[sequence], main_session=[], cool_down=[]
        )

        sequence_id = lesson_plan.warm_up[0].id

        set_id = uow.lesson_plans.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=5,
            duration_seconds=30,
            movement_variant=exercises.MovementVariant.STANDARD,
            equipment_variant=[],
        )

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 1
        assert plan.warm_up[0].sets[0].id == set_id
        assert plan.warm_up[0].sets[0].exercise_id == exercise.id
        assert plan.warm_up[0].sets[0].reps == 5
        assert plan.warm_up[0].sets[0].duration_seconds == 30
        assert (
            plan.warm_up[0].sets[0].movement_variant
            == exercises.MovementVariant.STANDARD
        )

    def test_adds_multiple_sets_to_same_sequence(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        exercise = exercise_helpers.Exercise.insert(uow)
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        sequence_id = lesson_plan.warm_up[0].id

        set_id_1 = uow.lesson_plans.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=5,
            duration_seconds=30,
            movement_variant=exercises.MovementVariant.STANDARD,
            equipment_variant=[],
        )
        set_id_2 = uow.lesson_plans.add_set_to_sequence(
            sequence_id=sequence_id,
            exercise_id=exercise.id,
            reps=10,
            duration_seconds=60,
            movement_variant=exercises.MovementVariant.PULSE,
            equipment_variant=[],
        )

        assert set_id_2 == set_id_1 + 1
        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 2
        assert plan.warm_up[0].sets[0].reps == 5
        assert plan.warm_up[0].sets[1].reps == 10

    def test_raises_exception_when_sequence_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        exercise = exercise_helpers.Exercise.insert(uow)

        with pytest.raises(lesson_plans.SequenceDoesNotExist) as exc_info:
            uow.lesson_plans.add_set_to_sequence(
                sequence_id=999,
                exercise_id=exercise.id,
                reps=5,
                duration_seconds=30,
                movement_variant=exercises.MovementVariant.STANDARD,
                equipment_variant=[],
            )

        assert exc_info.value.sequence_id == 999

    def test_raises_exception_when_exercise_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        sequence_id = lesson_plan.warm_up[0].id

        with pytest.raises(exercises.ExerciseDoesNotExist) as exc_info:
            uow.lesson_plans.add_set_to_sequence(
                sequence_id=sequence_id,
                exercise_id=999,
                reps=5,
                duration_seconds=30,
                movement_variant=exercises.MovementVariant.STANDARD,
                equipment_variant=[],
            )

        assert exc_info.value.exercise_id == 999


class TestGetExerciseSet:
    def test_returns_set_with_matching_id(self, uow: _unit_of_work.JSONUnitOfWork):
        exercise_set = lesson_plan_helpers.ExerciseSet(reps=5, duration_seconds=30)
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[exercise_set])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        set_id = lesson_plan.warm_up[0].sets[0].id

        result = uow.lesson_plans.get_exercise_set(set_id)

        assert result.id == set_id
        assert result.reps == 5
        assert result.duration_seconds == 30
        assert result.movement_variant == exercise_set.movement_variant

    def test_raises_exception_when_set_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.SetDoesNotExist) as exc_info:
            uow.lesson_plans.get_exercise_set(999)

        assert exc_info.value.set_id == 999


class TestUpdateExerciseSet:
    def test_updates_set_properties(self, uow: _unit_of_work.JSONUnitOfWork):
        exercise_set = lesson_plan_helpers.ExerciseSet(
            reps=5, duration_seconds=30, movement_variant="STANDARD"
        )
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[exercise_set])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        set_id = lesson_plan.warm_up[0].sets[0].id

        uow.lesson_plans.update_exercise_set(
            id=set_id,
            reps=10,
            duration_seconds=60,
            movement_variant=exercises.MovementVariant.PULSE,
            equipment_variant=[],
        )

        updated_set = uow.lesson_plans.get_exercise_set(set_id)
        assert updated_set.reps == 10
        assert updated_set.duration_seconds == 60
        assert updated_set.movement_variant == exercises.MovementVariant.PULSE

    def test_raises_exception_when_set_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.SetDoesNotExist) as exc_info:
            uow.lesson_plans.update_exercise_set(
                id=999,
                reps=10,
                duration_seconds=60,
                movement_variant=exercises.MovementVariant.PULSE,
                equipment_variant=[],
            )

        assert exc_info.value.set_id == 999


class TestDeleteExerciseSet:
    def test_deletes_set_from_sequence(self, uow: _unit_of_work.JSONUnitOfWork):
        set_1 = lesson_plan_helpers.ExerciseSet()
        set_2 = lesson_plan_helpers.ExerciseSet()
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[set_1, set_2])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        set_1_id = lesson_plan.warm_up[0].sets[0].id
        set_2_id = lesson_plan.warm_up[0].sets[1].id

        uow.lesson_plans.delete_exercise_set(set_1_id)

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up[0].sets) == 1
        assert plan.warm_up[0].sets[0].id == set_2_id

    def test_raises_exception_when_set_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.SetDoesNotExist) as exc_info:
            uow.lesson_plans.delete_exercise_set(999)

        assert exc_info.value.set_id == 999


class TestUpdateExerciseSequence:
    def test_updates_sequence_properties(self, uow: _unit_of_work.JSONUnitOfWork):
        sequence = lesson_plan_helpers.ExerciseSequence(
            name="Original Name", reps=1, notes="Original notes"
        )
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, warm_up=[sequence])

        sequence_id = lesson_plan.warm_up[0].id

        uow.lesson_plans.update_exercise_sequence(
            id=sequence_id,
            name="Updated Name",
            reps=3,
            notes="Updated notes",
        )

        updated_plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        updated_sequence = updated_plan.warm_up[0]
        assert updated_sequence.name == "Updated Name"
        assert updated_sequence.reps == 3
        assert updated_sequence.notes == "Updated notes"

    def test_preserves_sets_when_updating_sequence(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        set_1 = lesson_plan_helpers.ExerciseSet()
        set_2 = lesson_plan_helpers.ExerciseSet()
        sequence = lesson_plan_helpers.ExerciseSequence(
            name="Original Name", sets=[set_1, set_2]
        )
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, main_session=[sequence]
        )

        sequence_id = lesson_plan.main_session[0].id

        uow.lesson_plans.update_exercise_sequence(
            id=sequence_id,
            name="Updated Name",
            reps=2,
            notes="New notes",
        )

        updated_plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(updated_plan.main_session[0].sets) == 2
        assert updated_plan.main_session[0].sets[0].id == set_1.id
        assert updated_plan.main_session[0].sets[1].id == set_2.id

    def test_raises_exception_when_sequence_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.SequenceDoesNotExist) as exc_info:
            uow.lesson_plans.update_exercise_sequence(
                id=999,
                name="Test Name",
                reps=2,
                notes="Test notes",
            )

        assert exc_info.value.sequence_id == 999


class TestDeleteExerciseSequence:
    def test_deletes_sequence_from_section(self, uow: _unit_of_work.JSONUnitOfWork):
        sequence_1 = lesson_plan_helpers.ExerciseSequence()
        sequence_2 = lesson_plan_helpers.ExerciseSequence()
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(
            uow, warm_up=[sequence_1, sequence_2]
        )

        sequence_1_id = lesson_plan.warm_up[0].id
        sequence_2_id = lesson_plan.warm_up[1].id

        uow.lesson_plans.delete_exercise_sequence(sequence_1_id)

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.warm_up) == 1
        assert plan.warm_up[0].id == sequence_2_id

    def test_deletes_sequence_and_cascades_to_sets(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        set_1 = lesson_plan_helpers.ExerciseSet()
        set_2 = lesson_plan_helpers.ExerciseSet()
        sequence = lesson_plan_helpers.ExerciseSequence(sets=[set_1, set_2])
        lesson_plan = lesson_plan_helpers.LessonPlan.insert(uow, cool_down=[sequence])

        sequence_id = lesson_plan.cool_down[0].id
        set_1_id = lesson_plan.cool_down[0].sets[0].id
        set_2_id = lesson_plan.cool_down[0].sets[1].id

        uow.lesson_plans.delete_exercise_sequence(sequence_id)

        plan = uow.lesson_plans.get_lesson_plan(lesson_plan.id)
        assert len(plan.cool_down) == 0

        with pytest.raises(lesson_plans.SetDoesNotExist):
            uow.lesson_plans.get_exercise_set(set_1_id)

        with pytest.raises(lesson_plans.SetDoesNotExist):
            uow.lesson_plans.get_exercise_set(set_2_id)

    def test_raises_exception_when_sequence_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(lesson_plans.SequenceDoesNotExist) as exc_info:
            uow.lesson_plans.delete_exercise_sequence(999)

        assert exc_info.value.sequence_id == 999
