import contextlib
import typing
from unittest import mock

import pydantic

from pilates import config
from pilates.domain import vendors


OutputT = typing.TypeVar("OutputT", bound=pydantic.BaseModel)


class FakeCompletionClient(vendors.CompletionClient):
    def __init__(self, completion: pydantic.BaseModel):
        self._completion = completion

    @contextlib.contextmanager
    def inject(self) -> typing.Generator[None, None, None]:
        with mock.patch.object(config, "get_completion_client", return_value=self):
            yield

    async def get_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: type[OutputT],
    ) -> OutputT:
        return typing.cast(OutputT, self._completion)
