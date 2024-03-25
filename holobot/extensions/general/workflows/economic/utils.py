from holobot.discord.sdk.models import AutocompleteChoice, InteractionContext
from holobot.discord.sdk.workflows.interactables.models import AutocompleteOption
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.repositories import ICurrencyRepository

async def get_currency_autocomplete_choices(
    context: InteractionContext,
    options: tuple[AutocompleteOption, ...],
    target_option: AutocompleteOption,
    result_count_max: int,
    currency_repository: ICurrencyRepository,
    include_global: bool
) -> list[AutocompleteChoice]:
    if not isinstance(context, ServerChatInteractionContext):
        return []

    if not isinstance(target_option.value, str) or not target_option.value:
        currencies = await currency_repository.paginate_by_server(
            context.server_id,
            0,
            result_count_max,
            include_global
        )
        return [
            AutocompleteChoice(
                name=currency.name,
                value=str(currency.identifier)
            )
            for currency in currencies.items
        ]

    return [
        AutocompleteChoice(
            name=currency_name,
            value=str(currency_id)
        )
        for currency_id, currency_name in await currency_repository.search(
            target_option.value,
            context.server_id,
            result_count_max,
            include_global
        )
    ]
