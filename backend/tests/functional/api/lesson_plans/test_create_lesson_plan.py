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
