import pathlib
import uuid

import pydantic

from pilates.domain import templates, vendors


class PilatesClass(pydantic.BaseModel):
    warm_up: str
    main_session: str
    cool_down: str

    def render(self) -> str:
        return templates.render(
            directory="outputs",
            filename="lesson-plan.jinja",
            variables={"pilates_class": self},
        )


async def get_pilates_plan(
    *, user_prompt: str, client: vendors.OpenAICompletionClient | None = None
) -> str:
    client = client or vendors.OpenAICompletionClient()
    system_prompt = templates.render_system_prompt()

    pilates_class = await client.get_completion(
        system_prompt=system_prompt, user_prompt=user_prompt, output_format=PilatesClass
    )

    rendered_class = pilates_class.render()

    file_name = f"class-{uuid.uuid4()}.md"
    file_path = pathlib.Path(__file__).parents[-2] / "outputs" / file_name

    with open(file_path, "x") as f:
        f.write(rendered_class)

    return file_name
