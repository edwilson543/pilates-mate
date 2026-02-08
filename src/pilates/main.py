import asyncio

from . import _generation


async def async_main() -> None:
    instructions = "Generate a 45 minutes pilates class."
    file_name = await _generation.get_pilates_plan(user_prompt=instructions)
    print("Pilates plan saved to: ", file_name)


def main() -> None:
    """Synchronous entry point for the CLI script."""
    asyncio.run(async_main())

