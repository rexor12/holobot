from typing import TypeVar

from .constants import MANUALLY_GENERATED_KEY_NAME

T = TypeVar("T")

def manually_generated_key(wrapped_class: type[T]) -> type[T]:
    """A decorator for database records used to specify
    that primary key generation is manually performed,
    overriding the default behavior of letting the DBMS do it.

    :param wrapped_class: The record type to be marked.
    :type wrapped_class: type[T]
    :return: The same record type.
    :rtype: type[T]
    """

    setattr(wrapped_class, MANUALLY_GENERATED_KEY_NAME, True)
    return wrapped_class
