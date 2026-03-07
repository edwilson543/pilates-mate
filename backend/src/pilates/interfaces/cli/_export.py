import csv
import typing

import click

from pilates import config
from pilates.domain import exercises


@click.command("export-exercises")
@click.option(
    "--output",
    "-o",
    default="exercises.csv",
    type=click.Path(),
    help="Output CSV file path (default: exercises.csv)",
)
def export_exercises(*, output: str) -> None:
    """Export exercises from the database to a CSV file."""
    uow = config.get_unit_of_work()
    exercises_list = uow.exercises.get_exercises()

    if not exercises_list:
        click.echo("No exercises found to export.")
        return

    rows = [_convert_exercise_to_row(exercise) for exercise in exercises_list]
    fieldnames = rows[0].keys()

    with open(output, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    click.echo(f"Exported {len(rows)} exercises to {output}")


def _convert_exercise_to_row(
    exercise: exercises.Exercise,
) -> dict[str, typing.Any]:
    row = exercise.model_dump(exclude={"movement_variants", "equipment_variants"})
    for equipment in exercises.Equipment:
        row[equipment.value] = 1 if equipment in exercise.equipment_variants else 0
    for movement in exercises.MovementVariant:
        row[movement.value] = 1 if movement in exercise.movement_variants else 0

    return row
