import typing

import openai
import pydantic


OutputT = typing.TypeVar("OutputT", bound=pydantic.BaseModel)

class UnableToGetCompletion(Exception):
    pass

MODEL = "gpt-5-mini"
# MODEL = "gpt-4o-mini"


class OpenAICompletionClient:
    def __init__(self, model: str = MODEL):
        self._client = openai.AsyncClient()
        self._model = model

    async def get_completion(self, system_prompt: str, user_prompt: str, output_format: type[OutputT]) -> OutputT:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        try:
            response = await self._client.responses.parse(model=self._model, input=messages, text_format=output_format)
        except openai.APIError as exc:
            raise UnableToGetCompletion from exc

        return response.output_parsed
