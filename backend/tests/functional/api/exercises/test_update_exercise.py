from testing.helpers import lesson_plans as lesson_plan_helpers


def test_updates_exercise(api_client, unit_of_work):
    exercise = lesson_plan_helpers.Exercise.insert(unit_of_work)

    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": [],
    }
    update_response = api_client.put(f"/exercises/{exercise.id}", json=updated_exercise)

    assert update_response.status_code == 204
    assert update_response.content == b""

    get_response = api_client.get(f"/exercises/{exercise.id}")
    assert get_response.status_code == 200
    assert get_response.json() == {"id": exercise.id, **updated_exercise}


def test_update_response_not_found_when_exercise_does_not_exist(api_client):
    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": [],
    }

    response = api_client.put("/exercises/123", json=updated_exercise)

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}


def test_updating_exercise_updates_lesson_plan_references(api_client, unit_of_work):
    exercise = lesson_plan_helpers.Exercise.insert(unit_of_work)
    exercise_set = lesson_plan_helpers.ExerciseSet(exercise=exercise)
    sequence = lesson_plan_helpers.ExerciseSequence(sets=[exercise_set])
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(
        unit_of_work, warm_up=[sequence]
    )

    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": ["ANKLE_WEIGHTS"],
    }
    update_response = api_client.put(f"/exercises/{exercise.id}", json=updated_exercise)
    assert update_response.status_code == 204

    lesson_plan_response = api_client.get(f"/lesson-plans/{lesson_plan.id}")
    assert lesson_plan_response.status_code == 200

    warm_up_exercise = lesson_plan_response.json()["warm_up"][0]["sets"][0]["exercise"]
    assert warm_up_exercise["id"] == exercise.id
    assert warm_up_exercise["name"] == "Jump Squats"
    assert warm_up_exercise["description"] == "Move up and down with a jump"
    assert warm_up_exercise["difficulty"] == "ADVANCED"
    assert warm_up_exercise["movement_variants"] == ["STANDARD", "PULSE"]
    assert warm_up_exercise["equipment_variants"] == ["ANKLE_WEIGHTS"]
