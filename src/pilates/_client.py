import typing

import openai
import pydantic


OutputT = typing.TypeVar("OutputT", bound=pydantic.BaseModel)

class UnableToGetCompletion(Exception):
    pass

class OpenAICompletionClient:
    def __init__(self, model: str = "gpt-5.2"):
        self._client = openai.AsyncClient()
        self._model = model

    async def get_completion(self, system_prompt: str, user_prompt: str, output_format: type[OutputT]) -> OutputT:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        try:
            return await self._client.responses.parse(model=self._model, input=messages, text_format=output_format)
        except openai.APIError as exc:
            raise UnableToGetCompletion from exc

