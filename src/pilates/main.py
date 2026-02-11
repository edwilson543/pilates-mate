import asyncio

from pilates import config
from pilates.application import generate_plan


async def async_main() -> None:
    instructions = "Generate a 45 minutes pilates class."
    client = config.get_completion_client()
    file_name = await generate_plan.get_pilates_plan(
        client=client, user_prompt=instructions
    )
    print("Pilates plan saved to: ", file_name)


def main() -> None:
    """Synchronous entry point for the CLI script."""
    asyncio.run(async_main())
