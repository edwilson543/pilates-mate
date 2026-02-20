import datetime as dt

from pilates import config
from pilates.domain import lesson_planning


def test_creates_then_gets_lesson_plan(api_client):
    lesson_plan_list = api_client.get("/lesson-plans")

    assert lesson_plan_list.status_code == 200
    assert lesson_plan_list.json() == []

    repository = config.get_lesson_planning_repository()
    exercise_id = repository.create_exercise(
        name="Hundred",
        description="Classic Pilates breathing exercise",
        difficulty=lesson_planning.Difficulty.BEGINNER,
        primary_muscle_group=lesson_planning.MuscleGroup.CORE,
        starting_position=lesson_planning.StartingPosition.SUPINE,
        variants=[lesson_planning.ExerciseVariant.STANDARD],
    )
    lesson_plan_id = repository.create_lesson_plan(
        name="Morning Flow",
        description="A refreshing morning Pilates session",
        date=dt.date(2026, 1, 15),
    )
    warm_up_seq = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.WARM_UP,
        name="Breathing",
        reps=1,
        notes="Warm up notes",
    )
    repository.add_set_to_sequence(
        sequence_id=warm_up_seq,
        exercise_id=exercise_id,
        reps=10,
        duration_seconds=60,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )
    main_seq = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.MAIN_SESSION,
        name="Core Work",
        reps=3,
        notes="Main session notes",
    )
    repository.add_set_to_sequence(
        sequence_id=main_seq,
        exercise_id=exercise_id,
        reps=10,
        duration_seconds=60,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )
    cool_down_seq = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.COOL_DOWN,
        name="Stretching",
        reps=1,
        notes="Cool down notes",
    )
    repository.add_set_to_sequence(
        sequence_id=cool_down_seq,
        exercise_id=exercise_id,
        reps=5,
        duration_seconds=30,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )

    lesson_plan = api_client.get(f"/lesson-plans/{lesson_plan_id}")

    assert lesson_plan.status_code == 200
    lesson_plan_json = lesson_plan.json()
    assert lesson_plan_json["id"] == lesson_plan_id
    assert lesson_plan_json["name"] == "Morning Flow"
    assert lesson_plan_json["description"] == "A refreshing morning Pilates session"
    assert len(lesson_plan_json["warm_up"]) == 1
    assert len(lesson_plan_json["main_session"]) == 1
    assert len(lesson_plan_json["cool_down"]) == 1

    updated_lesson_plan_list = api_client.get("/lesson-plans")

    assert updated_lesson_plan_list.status_code == 200
    assert len(updated_lesson_plan_list.json()) == 1
    assert updated_lesson_plan_list.json()[0] == lesson_plan_json


def test_response_not_found_when_lesson_plan_does_not_exist(api_client):
    lesson_plan_id = 123

    response = api_client.get(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}


def test_deletes_lesson_plan(api_client):
    repository = config.get_lesson_planning_repository()
    lesson_plan_id = repository.create_lesson_plan(
        name="Morning Flow",
        description="A refreshing morning Pilates session",
        date=dt.date(2026, 1, 15),
    )

    response = api_client.delete(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 204
    assert response.content == b""

    lesson_plan_list = api_client.get("/lesson-plans")
    assert lesson_plan_list.status_code == 200
    assert lesson_plan_list.json() == []


def test_delete_response_not_found_when_lesson_plan_does_not_exist(api_client):
    lesson_plan_id = 123

    response = api_client.delete(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}
