from collections.abc import Iterable
from typing import Any

from holobot.sdk.i18n.ii18n_provider import II18nProvider

class FakeI18nProvider(II18nProvider):
    def get(
        self,
        key: str,
        arguments: dict[str, Any] | None = None,
        language: str | None = None,
    ) -> str:
        return key

    def get_list(
        self,
        key: str,
        language: str | None = None,
    ) -> tuple[str, ...]:
        return ()

    def get_list_item(
        self,
        key: str,
        item_index: int,
        arguments: dict[str, Any] | None = None,
        language: str | None = None
    ) -> str:
        return key

    def get_list_items(
        self,
        key: str,
        item_arguments: Iterable[dict[str, Any]],
        language: str | None = None
    ) -> tuple[str, ...]:
        return ()

    def get_random_list_item(
        self,
        key: str,
        language: str | None = None
    ) -> str:
        return key
