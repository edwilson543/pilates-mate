import json
import pathlib

import click

from pilates import config
from pilates.domain import lesson_plans
from pilates.interfaces.cli._main import async_command


@click.command("evaluate-prompt")
@click.option(
    "--version",
    "-v",
    default="v1",
    help="Template version to evaluate (default: v1)",
)
@async_command
async def evaluate_prompt(*, version: str) -> None:
    """Evaluate system prompt template across multiple test scenarios."""
    click.echo(f"Evaluating template version: {version}")

    deps = config.get_evaluation_deps()
    result = await lesson_plans.evaluate_system_prompt(version=version, deps=deps)

    output_dir = _get_output_dir(version)

    with open(output_dir / "benchmark.md", "w") as f:
        f.write(result.render())

    with open(output_dir / "benchmark.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    with open(output_dir / "rendered.md", "w") as f:
        f.write(lesson_plans.render_sample_system_prompt(version=version, deps=deps))

    click.echo(f"Evaluation saved to {output_dir}")


def _get_output_dir(version: str) -> pathlib.Path:
    return (
        pathlib.Path(__file__).parents[2]
        / "domain"
        / "templates"
        / "lesson-planning"
        / version
    )
