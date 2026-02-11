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

    async def get_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: type[OutputT],
    ) -> OutputT:
        return typing.cast(OutputT, self._completion)


@contextlib.contextmanager
def install_fake_completion_client(
    completion: pydantic.BaseModel,
) -> typing.Generator[None, None, None]:
    client = FakeCompletionClient(completion=completion)

    with mock.patch.object(config, "get_completion_client", return_value=client):
        yield
