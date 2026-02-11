import abc
import typing

import pydantic


OutputT = typing.TypeVar("OutputT", bound=pydantic.BaseModel)


class UnableToGetCompletion(Exception):
    pass


class CompletionClient(abc.ABC):
    @abc.abstractmethod
    async def get_completion(
        self, system_prompt: str, user_prompt: str, output_format: type[OutputT]
    ) -> OutputT:
        """
        Get a completion.

        :raises UnableToGetCompletion: If the request fails for some reason
        """
        raise NotImplementedError
