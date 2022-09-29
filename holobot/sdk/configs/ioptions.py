from typing import Protocol, TypeVar

from .options_definition import OptionsDefinition

TOptions = TypeVar("TOptions", bound=OptionsDefinition, covariant=True)

class IOptions(Protocol[TOptions]):
    """Interface for a configuration options provider."""

    @property
    def value(self) -> TOptions:
        """Gets the configured options.

        :return: The configured options.
        :rtype: TOptions
        """
        ...
