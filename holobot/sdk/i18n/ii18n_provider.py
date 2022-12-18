from collections.abc import Sequence
from typing import Any, Protocol

class II18nProvider(Protocol):
    """Interface for a service used to resolve internationalization keys."""

    def get(
        self,
        key: str,
        arguments: dict[str, Any] | None = None,
        language: str | None = None,
    ) -> str:
        """Gets the formatted text associated to the specified key.

        - If there is no value associated to the specified key, the key is returned.
        - If there is no value associated to the specified key in the specified language,
        the default translation is returned (or the key, as per the above).

        :param key: The I18N key used to identify the resource.
        :type key: str
        :param arguments: An optional key-value pair collection to resolve text templates, defaults to None
        :type arguments: dict[str, Any] | None, optional
        :param language: An optional language for which to get the translation, defaults to None
        :type language: str | None, optional
        :return: The formatted text or the key itself if there is no associated value.
        :rtype: str
        """
        ...

    def get_list(
        self,
        key: str,
        language: str | None = None,
    ) -> tuple[str, ...]:
        """Gets a list of strings associated to the specified key.

        - If there is no value associated to the specified key, an empty list is returned.
        - If there is no value associated to the specified key in the specified language,
        the default translation is returned (or an empty list, as per the above).

        :param key: The I18N key used to identify the resource.
        :type key: str
        :param language: An optional language for which to get the translation, defaults to None
        :type language: str | None, optional
        :return: The list of strings or an empty list if there is no associated value.
        :rtype: tuple[str, ...]
        """
        ...

    def get_list_item(
        self,
        key: str,
        item_index: int,
        arguments: dict[str, Any] | None = None,
        language: str | None = None
    ) -> str:
        """Gets the formatted text associated to the specified key and index of a list.

        - If there is no value associated to the specified key, the key is returned.
        - If there is no value associated to the specified key in the specified language,
        the default translation is returned (or the key, as per the above).
        - If the specified index falls outside the range of items, the key is returned.

        :param key: The I18N key used to identify the resource.
        :type key: str
        :type item_index: int
        :param item_index: The index of the item in the list of values.
        :param arguments: An optional key-value pair collection to resolve text templates, defaults to None
        :type arguments: dict[str, Any] | None, optional
        :param language: An optional language for which to get the translation, defaults to None
        :type language: str | None, optional
        :return: The formatted text or the key itself if there is no associated value.
        :rtype: str
        """
        ...

    def get_list_items(
        self,
        key: str,
        item_arguments: Sequence[dict[str, Any]],
        language: str | None = None
    ) -> tuple[str, ...]:
        """Gets a list of formatted strings associated to the specified key.

        - If there is no value associated to the specified key, an empty list is returned.
        - If there is no value associated to the specified key in the specified language,
        the default translation is returned (or an empty list, as per the above).

        This is essentially the same as resolving the same key for multiple values one by one,
        but an effort is made to avoid multiple look-ups.

        :param key: The I18N key used to identify the resource.
        :type key: str
        :param item_arguments: A list of key-value pair collections to resolve text templates for each item, defaults to None
        :type item_arguments: Sequence[dict[str, Any]]
        :param language: An optional language for which to get the translation, defaults to None
        :type language: str | None, optional
        :return: The list of formatted strings or an empty list if there is no associated value.
        :rtype: tuple[str, ...]
        """
        ...
