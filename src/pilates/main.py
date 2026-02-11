import asyncio

from pilates import config
from pilates.application import generate_plan


async def async_main() -> None:
    instructions = "Generate a 45 minutes pilates class."
    client = config.get_completion_client()
    repository = config.get_lesson_planning_repository()
    lesson_plan = await generate_plan.generate_lesson_plan(
        client=client, user_prompt=instructions, repository=repository
    )
    print("Pilates plan saved with ID: ", lesson_plan.id)


def main() -> None:
    """Synchronous entry point for the CLI script."""
    asyncio.run(async_main())
