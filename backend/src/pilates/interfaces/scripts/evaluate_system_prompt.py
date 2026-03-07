import argparse
import asyncio

from pilates import config
from pilates.domain import lesson_plans


async def main():
    parser = argparse.ArgumentParser(
        description="Evaluate system prompt template across multiple test scenarios."
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="Template version to evaluate (default: v1)",
    )
    args = parser.parse_args()

    print(f"Evaluating template version: {args.version}")
    print()

    deps = config.get_evaluation_deps()

    result = await lesson_plans.evaluate_system_prompt(version=args.version, deps=deps)
    print(result.render())


if __name__ == "__main__":
    asyncio.run(main())
