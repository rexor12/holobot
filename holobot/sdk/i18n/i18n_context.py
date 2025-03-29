from collections.abc import Iterable
from typing import Any, ClassVar

from holobot.sdk.ioc.decorators import injectable
from .ii18n_provider import II18nProvider

@injectable(None)
class I18nContext:
    """
    Keeps a reference to the `II18nProvider` provided to an instance of this class.
    The associated utility methods can be used anywhere - provided the `II18nProvider`
    instance has been created already - to proxy calls to that instance.
    This way, workflows, for example, don't have to depend on `II18nProvider` directly.

    NOTE: This works because II18nProvider is not a scoped service.
    """

    # Dependency injection will initialize this.
    i18n_provider: ClassVar[II18nProvider | None] = None

    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        I18nContext.i18n_provider = i18n_provider

def localize(
    key: str,
    arguments: dict[str, Any] | None = None,
    language: str | None = None,
) -> str:
    assert I18nContext.i18n_provider is not None
    return I18nContext.i18n_provider.get(key, arguments, language)

def localize_list(
    key: str,
    language: str | None = None,
) -> tuple[str, ...]:
    assert I18nContext.i18n_provider is not None
    return I18nContext.i18n_provider.get_list(key, language)

def localize_list_item(
    key: str,
    item_index: int,
    arguments: dict[str, Any] | None = None,
    language: str | None = None
) -> str:
    assert I18nContext.i18n_provider is not None
    return I18nContext.i18n_provider.get_list_item(key, item_index, arguments, language)

def localize_list_items(
    key: str,
    item_arguments: Iterable[dict[str, Any]],
    language: str | None = None
) -> tuple[str, ...]:
    assert I18nContext.i18n_provider is not None
    return I18nContext.i18n_provider.get_list_items(key, item_arguments, language)

def localize_random_list_item(
    key: str,
    language: str | None = None
) -> str:
    assert I18nContext.i18n_provider is not None
    return I18nContext.i18n_provider.get_random_list_item(key, language)
