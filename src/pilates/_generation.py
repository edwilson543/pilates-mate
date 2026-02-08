from . import _client
import pydantic

class PilatesClass(pydantic.BaseModel):
    warm_up: str
    main_session: str
    cool_down: str


def get_pilates_plan(*, user_prompt: str, client: _client.OpenAICompletionClient | None = None) -> PilatesClass:
    client = client or _client.OpenAICompletionClient()
    sytem_prompt

    client.get_completion()
