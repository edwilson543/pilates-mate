import asyncio
import functools

import click


def async_command(f):
    """Decorator to run async Click commands with asyncio.run()."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    """Pilates lesson plan management CLI."""
    pass


def _register_commands():
    """Register all CLI commands with the main group."""
    from . import _evaluation, _export, _optimisation

    cli.add_command(_export.export_exercises)
    cli.add_command(_evaluation.evaluate_prompt)
    cli.add_command(_optimisation.optimise_prompt)


_register_commands()
