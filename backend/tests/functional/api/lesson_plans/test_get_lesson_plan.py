from testing.helpers import lesson_plans as lesson_plan_helpers


def test_creates_then_gets_lesson_plan(authenticated_api_client, unit_of_work):
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(unit_of_work)

    get_lesson_plans = authenticated_api_client.get(f"/lesson-plans/{lesson_plan.id}")

    assert get_lesson_plans.status_code == 200
    lesson_plan_json = get_lesson_plans.json()
    assert lesson_plan_json["id"] == lesson_plan.id
    assert lesson_plan_json["name"] == lesson_plan.name
    assert lesson_plan_json["description"] == lesson_plan.description
    assert len(lesson_plan_json["warm_up"]) == len(lesson_plan.warm_up)

    updated_lesson_plan_list = authenticated_api_client.get("/lesson-plans")

    assert updated_lesson_plan_list.status_code == 200
    assert len(updated_lesson_plan_list.json()) == 1
    assert updated_lesson_plan_list.json()[0] == lesson_plan_json


def test_response_not_found_when_lesson_plan_does_not_exist(authenticated_api_client):
    lesson_plan_id = 123

    response = authenticated_api_client.get(f"/lesson-plans/{lesson_plan_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}
