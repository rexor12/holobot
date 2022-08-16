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
