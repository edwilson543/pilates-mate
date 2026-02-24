from testing.helpers import lesson_plans as lesson_plan_helpers


def test_deletes_lesson_plan(api_client, repository):
    lesson_plan = lesson_plan_helpers.LessonPlan.create_in_repo(repository)

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
