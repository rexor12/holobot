from typing import Callable, Generic, TypeVar

T = TypeVar("T")

class CancellationTokenRegistration(Generic[T]):
    """Represents a callback registration to a cancellation token.

    :param Generic: The type of the state object.
    :type Generic: Generic[T]
    """

    def __init__(self, identifier: int, callback: Callable[[T], None], state: T) -> None:
        super().__init__()
        self.__identifier: int = identifier
        self.__callback: Callable[[T], None] = callback
        self.__state: T = state

    @property
    def identifier(self) -> int:
        """Gets the identifier associated to this registration.

        This identifier is unique between registrations
        of a single cancellation token only.

        :return: The identifier of the registration.
        :rtype: int
        """

        return self.__identifier

    @property
    def callback(self) -> Callable[[T], None]:
        """Gets the callback method.

        :return: The callback method.
        :rtype: Callable[[T], None]
        """

        return self.__callback

    @property
    def state(self) -> T:
        """Gets the state to be passed to the callback.

        :return: The associated state.
        :rtype: T
        """

        return self.__state
