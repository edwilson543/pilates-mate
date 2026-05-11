import abc
import typing

import pydantic


CompletionT = typing.TypeVar("CompletionT", bound=pydantic.BaseModel)


class UnableToGetCompletion(Exception):
    pass


class CompletionClient(abc.ABC):
    @abc.abstractmethod
    async def get_completion(
        self, system_prompt: str, user_prompt: str, output_format: type[CompletionT]
    ) -> CompletionT:
        """
        Get a completion.

        :raises UnableToGetCompletion: If the request fails for some reason
        """
        raise NotImplementedError
