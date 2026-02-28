import pathlib
import typing

import jinja2


def render(*, directory: str, filename: str, variables: dict[str, typing.Any]) -> str:
    prompts_dir = pathlib.Path(__file__).parent / directory

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(prompts_dir),
        autoescape=jinja2.select_autoescape(),
        undefined=jinja2.StrictUndefined,
    )
    template = env.get_template(filename)
    return template.render(**variables)
