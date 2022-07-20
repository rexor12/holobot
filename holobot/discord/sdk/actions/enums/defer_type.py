from enum import IntEnum, unique

@unique
class DeferType(IntEnum):
    """Defines the valid types of a deferred response."""

    NONE = 0
    """No initial response is created and a response is expected soon."""

    DEFER_MESSAGE_CREATION = 1
    """Creates an initial response to acknowledge the request
    - and display the loading indicator - with the intention to
    create a new message later as the response.
    """

    DEFER_MESSAGE_UPDATE = 2
    """Creates an initial response to acknowledge the request
    - and display the loading indicator - with the intention to
    update the existing message later as the response.
    """
