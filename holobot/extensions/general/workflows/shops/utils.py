from collections.abc import Awaitable

from holobot.discord.sdk.models import AutocompleteChoice
from holobot.discord.sdk.workflows.interactables.models import AutocompleteOption
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.managers import IShopManager

def autocomplete_shop(
    shop_manager: IShopManager,
    context: ServerChatInteractionContext,
    target_option: AutocompleteOption,
    option_count_max: int = 5
) -> Awaitable[list[AutocompleteChoice]]:
    return __get_shop_autocomplete_options(
        shop_manager,
        context.server_id,
        (
            target_option.value
            if isinstance(target_option.value, str) and target_option.value
            else None
        ),
        option_count_max
    )

def autocomplete_global_shop(
    shop_manager: IShopManager,
    target_option: AutocompleteOption,
    option_count_max: int = 5
) -> Awaitable[list[AutocompleteChoice]]:
    return __get_shop_autocomplete_options(
        shop_manager,
        0,
        (
            target_option.value
            if isinstance(target_option.value, str) and target_option.value
            else None
        ),
        option_count_max
    )

async def __get_shop_autocomplete_options(
    shop_manager: IShopManager,
    server_id: int,
    search_text: str | None,
    option_count_max: int
) -> list[AutocompleteChoice]:
    shop_infos = await shop_manager.paginate_shops(
        server_id,
        search_text,
        0,
        option_count_max
    )

    return [
        AutocompleteChoice(
            name=shop_info.name,
            value=str(shop_info.identifier)
        ) for shop_info in shop_infos.items
    ]
