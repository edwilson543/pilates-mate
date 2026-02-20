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


def test_add_set_to_sequence(api_client):
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
    sequence_id = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.WARM_UP,
        name="Breathing",
        reps=1,
        notes="Warm up notes",
    )

    response = api_client.post(
        f"/lesson-plans/sequences/{sequence_id}/sets",
        json={
            "exercise_id": exercise_id,
            "reps": 10,
            "duration_seconds": 60,
            "variant": "STANDARD",
        },
    )

    assert response.status_code == 201
    set_id = response.json()["id"]
    assert set_id == 1

    lesson_plan = repository.get_lesson_plan(lesson_plan_id)
    assert len(lesson_plan.warm_up[0].sets) == 1
    assert lesson_plan.warm_up[0].sets[0].id == set_id
    assert lesson_plan.warm_up[0].sets[0].reps == 10


def test_update_exercise_set(api_client):
    repository = config.get_lesson_planning_repository()
    exercise_id = repository.create_exercise(
        name="Hundred",
        description="Classic Pilates breathing exercise",
        difficulty=lesson_planning.Difficulty.BEGINNER,
        primary_muscle_group=lesson_planning.MuscleGroup.CORE,
        starting_position=lesson_planning.StartingPosition.SUPINE,
        variants=[
            lesson_planning.ExerciseVariant.STANDARD,
            lesson_planning.ExerciseVariant.PULSE,
        ],
    )
    lesson_plan_id = repository.create_lesson_plan(
        name="Morning Flow",
        description="A refreshing morning Pilates session",
        date=dt.date(2026, 1, 15),
    )
    sequence_id = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.WARM_UP,
        name="Breathing",
        reps=1,
        notes="Warm up notes",
    )
    set_id = repository.add_set_to_sequence(
        sequence_id=sequence_id,
        exercise_id=exercise_id,
        reps=5,
        duration_seconds=30,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )

    response = api_client.put(
        f"/lesson-plans/sequences/{sequence_id}/sets/{set_id}",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "variant": "PULSE",
        },
    )

    assert response.status_code == 204
    assert response.content == b""

    updated_set = repository.get_exercise_set(set_id)
    assert updated_set.reps == 10
    assert updated_set.duration_seconds == 60
    assert updated_set.variant == lesson_planning.ExerciseVariant.PULSE


def test_delete_exercise_set(api_client):
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
    sequence_id = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.WARM_UP,
        name="Breathing",
        reps=1,
        notes="Warm up notes",
    )
    set_id_1 = repository.add_set_to_sequence(
        sequence_id=sequence_id,
        exercise_id=exercise_id,
        reps=5,
        duration_seconds=30,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )
    set_id_2 = repository.add_set_to_sequence(
        sequence_id=sequence_id,
        exercise_id=exercise_id,
        reps=10,
        duration_seconds=60,
        variant=lesson_planning.ExerciseVariant.PULSE,
    )

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence_id}/sets/{set_id_1}"
    )

    assert response.status_code == 204
    assert response.content == b""

    lesson_plan = repository.get_lesson_plan(lesson_plan_id)
    assert len(lesson_plan.warm_up[0].sets) == 1
    assert lesson_plan.warm_up[0].sets[0].id == set_id_2


def test_update_nonexistent_set_returns_404(api_client):
    response = api_client.put(
        "/lesson-plans/sequences/999/sets/999",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "variant": "PULSE",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}


def test_delete_nonexistent_set_returns_404(api_client):
    response = api_client.delete("/lesson-plans/sequences/999/sets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
