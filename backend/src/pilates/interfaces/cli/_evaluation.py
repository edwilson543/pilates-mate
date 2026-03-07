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

    click.echo(result.render())
