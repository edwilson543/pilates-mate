import csv

from pilates.interfaces.cli._main import cli
from testing.helpers import exercises as exercise_helpers


def test_exports_exercises_to_default_file(cli_runner, unit_of_work, tmp_path):
    exercise_helpers.Exercise.insert(unit_of_work)
    exercise_helpers.Exercise.insert(unit_of_work)

    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(cli, ["export-exercises"])

    assert result.exit_code == 0
    assert "Exported 2 exercises" in result.output


def test_exports_exercises_to_custom_output_file(cli_runner, unit_of_work, tmp_path):
    exercise = exercise_helpers.Exercise.insert(unit_of_work)

    output_file = tmp_path / "custom.csv"
    result = cli_runner.invoke(cli, ["export-exercises", "--output", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify CSV structure.
    with open(output_file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["name"] == exercise.name


def test_exports_no_exercises_gracefully(cli_runner, unit_of_work, tmp_path):
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(cli, ["export-exercises"])

    assert result.exit_code == 0
    assert "No exercises found to export" in result.output
