from pilates.domain import lesson_planning
from testing.helpers import lesson_planning as lesson_planning_helpers


def test_creates_then_gets_lesson_plan(api_client, repository):
    list_lesson_plans = api_client.get("/lesson-plans")

    assert list_lesson_plans.status_code == 200
    assert list_lesson_plans.json() == []

    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(repository)

    get_lesson_plans = api_client.get(f"/lesson-plans/{lesson_plan.id}")

    assert get_lesson_plans.status_code == 200
    lesson_plan_json = get_lesson_plans.json()
    assert lesson_plan_json["id"] == lesson_plan.id
    assert lesson_plan_json["name"] == lesson_plan.name
    assert lesson_plan_json["description"] == lesson_plan.description
    assert lesson_plan_json["warm_up"] == lesson_plan.model_dump(mode="json")["warm_up"]

    updated_lesson_plan_list = api_client.get("/lesson-plans")

    assert updated_lesson_plan_list.status_code == 200
    assert len(updated_lesson_plan_list.json()) == 1
    assert updated_lesson_plan_list.json()[0] == lesson_plan_json


def test_response_not_found_when_lesson_plan_does_not_exist(api_client):
    lesson_plan_id = 123

    response = api_client.get(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}


def test_deletes_lesson_plan(api_client, repository):
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(repository)

    response = api_client.delete(f"/lesson-plans/{lesson_plan.id}")

    assert response.status_code == 204

    lesson_plan_list = api_client.get("/lesson-plans")

    assert lesson_plan_list.status_code == 200
    assert lesson_plan_list.json() == []


def test_delete_response_not_found_when_lesson_plan_does_not_exist(api_client):
    lesson_plan_id = 123

    response = api_client.delete(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}


def test_adds_exercise_set_to_existing_sequence(api_client, repository):
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[])
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, warm_up=[sequence]
    )
    exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)

    response = api_client.post(
        f"/lesson-plans/sequences/{sequence.id}/sets",
        json={
            "exercise_id": exercise.id,
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "STANDARD",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 201
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    new_set = lesson_plan.warm_up[0].sets[0]
    assert response.json()["id"] == new_set.id

    assert new_set.exercise.id == exercise.id
    assert new_set.reps == 10
    assert new_set.duration_seconds == 60
    assert new_set.movement_variant == "STANDARD"


def test_update_exercise_set_to_new_values(api_client, repository):
    exercise_set = lesson_planning_helpers.ExerciseSet(
        reps=31, duration_seconds=30, movement_variant="HOLD"
    )
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[exercise_set])
    lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, main_session=[sequence]
    )

    response = api_client.put(
        f"/lesson-plans/sequences/{sequence.id}/sets/{exercise_set.id}",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "PULSE",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 204

    updated_set = repository.get_exercise_set(exercise_set.id)
    assert updated_set.reps == 10
    assert updated_set.duration_seconds == 60
    assert updated_set.movement_variant == lesson_planning.MovementVariant.PULSE


def test_response_not_found_when_updating_nonexistent_set(api_client):
    response = api_client.put(
        "/lesson-plans/sequences/999/sets/999",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "PULSE",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}


def test_deletes_existing_exercise_sets(repository, api_client):
    first_set = lesson_planning_helpers.ExerciseSet()
    second_set = lesson_planning_helpers.ExerciseSet()
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[first_set, second_set])
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, cool_down=[sequence]
    )

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{first_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == [second_set]

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{second_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == []


def test_response_not_found_when_deleting_nonexistent_set(api_client):
    response = api_client.delete("/lesson-plans/sequences/999/sets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
