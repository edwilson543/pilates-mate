import openai

from . import _base


class OpenAICompletionClient(_base.CompletionClient):
    def __init__(self, *, api_key: str, model: str):
        self._client = openai.AsyncClient(api_key=api_key)
        self._model = model

    async def get_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: type[_base.CompletionT],
    ) -> _base.CompletionT:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        try:
            response = await self._client.responses.parse(
                model=self._model,
                input=messages,  # type: ignore[arg-type]
                text_format=output_format,
            )
        except openai.APIError as exc:
            raise _base.UnableToGetCompletion from exc

        if not (outputs := response.output_parsed):
            raise _base.UnableToGetCompletion("API did not return any outputs.")

        return outputs
