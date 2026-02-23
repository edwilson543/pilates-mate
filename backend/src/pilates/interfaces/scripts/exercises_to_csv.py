import csv
import typing

from pilates import config
from pilates.domain import lesson_planning


def main():
    """
    Export the exercises from the database to a CSV file at `./exercises.csv`.
    """
    repo = config.get_lesson_planning_repository()
    exercises = repo.get_exercises()
    rows = [_convert_exercise_to_row(exercise) for exercise in exercises]

    fieldnames = rows[0].keys()

    with open("exercises.csv", "x", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _convert_exercise_to_row(
    exercise: lesson_planning.Exercise,
) -> dict[str, typing.Any]:
    row = exercise.model_dump(exclude={"movement_variants", "equipment_variants"})
    for equipment in lesson_planning.Equipment:
        row[equipment.value] = 1 if equipment in exercise.equipment_variants else 0
    for movement in lesson_planning.MovementVariant:
        row[movement.value] = 1 if movement in exercise.movement_variants else 0

    return row


if __name__ == "__main__":
    main()
