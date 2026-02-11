import pathlib
import typing

import jinja2


def render_system_prompt(
    *, exercises: list[typing.Any], example_lesson_plans: list[typing.Any]
) -> str:
    return render(
        directory="prompts",
        filename="system.jinja",
        variables={
            "exercises": exercises,
            "example_lesson_plans": example_lesson_plans,
        },
    )


def render(*, directory: str, filename: str, variables: dict[str, typing.Any]) -> str:
    prompts_dir = pathlib.Path(__file__).parent / directory

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(prompts_dir),
        autoescape=jinja2.select_autoescape(),
    )
    template = env.get_template(filename)
    return template.render(**variables)
