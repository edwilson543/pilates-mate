import uuid
import pathlib
from idlelib.browser import file_open

import jinja2
import pydantic


from . import _client, _prompts


class PilatesClass(pydantic.BaseModel):
    warm_up: str
    main_session: str
    cool_down: str

    def render(self) -> str:
        current_dir = pathlib.Path(__file__).parent
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(current_dir), autoescape=jinja2.select_autoescape()
        )
        template = env.get_template("outputs.jinja")
        return template.render(pilates_class=self)


async def get_pilates_plan(
    *, user_prompt: str, client: _client.OpenAICompletionClient | None = None
) -> str:
    client = client or _client.OpenAICompletionClient()
    system_prompt = _prompts.render_system_prompt()

    pilates_class = await client.get_completion(
        system_prompt=system_prompt, user_prompt=user_prompt, output_format=PilatesClass
    )

    rendered_class = pilates_class.render()

    file_name = f"class-{uuid.uuid4()}.md"
    file_path = pathlib.Path(__file__).parent / "outputs" / file_name

    with open(file_path, "x") as f:
        f.write(rendered_class)

    return file_name
