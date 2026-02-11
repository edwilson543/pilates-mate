from pilates import config
from testing.helpers import lesson_planning as lesson_planning_helpers


def test_creates_then_gets_lesson_plan(api_client):
    lesson_plan_list = api_client.get("/lesson-plans")

    assert lesson_plan_list.status_code == 200
    assert lesson_plan_list.json() == []

    repository = config.get_lesson_planning_repository()
    lesson_plan_id = repository.create_lesson_plan(
        name="Morning Flow",
        description="A refreshing morning Pilates session",
        warm_up=[lesson_planning_helpers.ExerciseSequence()],
        main_session=[lesson_planning_helpers.ExerciseSequence()],
        cool_down=[lesson_planning_helpers.ExerciseSequence()],
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
