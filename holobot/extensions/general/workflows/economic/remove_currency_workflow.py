from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.repositories import ICurrencyRepository
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveCurrencyWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__i18n = i18n_provider

    @component(
        identifier="gn_currency_del",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def remove_currency(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (currency_id_str := state.custom_data.get("i"))
            or not (currency_id := int(currency_id_str))
        ):
            return self._edit_message(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                embed=None
            )

        if not (currency := await self.__currency_repository.try_get_by_server(currency_id, context.server_id, False)):
            return self._edit_message(
                content=self.__i18n.get("extensions.general.remove_currency_workflow.invalid_currency_error"),
                embed=None
            )

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.remove_currency_workflow.remove_confirmation",
                {
                    "currency_name": currency.name
                }
            ),
            components=[
                StackLayout(
                    id="dummy",
                    children=[
                        Button(
                            id="gn_currency_dely",
                            owner_id=state.owner_id,
                            text=self.__i18n.get("common.buttons.yes"),
                            style=ComponentStyle.DANGER,
                            custom_data={
                                "i": str(currency_id)
                            }
                        ),
                        Button(
                            id="gn_currency_deln",
                            owner_id=state.owner_id,
                            text=self.__i18n.get("common.buttons.no"),
                            style=ComponentStyle.SECONDARY
                        ),
                    ]
                )
            ],
            embed=None
        )

    @component(
        identifier="gn_currency_dely",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def confirm_currency_removal(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (currency_id_str := state.custom_data.get("i"))
            or not (currency_id := int(currency_id_str))
        ):
            return self._edit_message(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                embed=None
            )

        await self.__currency_repository.delete_by_server(int(currency_id), context.server_id)

        return self._edit_message(
            content=self.__i18n.get("extensions.general.remove_currency_workflow.currency_removed_successfully"),
            components=Button(
                id="gn_currency_view",
                owner_id=context.author_id,
                text=self.__i18n.get("extensions.general.remove_currency_workflow.view_currencies_button")
            ),
            embed=None
        )

    @component(
        identifier="gn_currency_deln",
        is_bound=True,
        required_permissions=Permission.ADMINISTRATOR
    )
    async def decline_currency_removal(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._edit_message(
            content=self.__i18n.get("extensions.general.remove_currency_workflow.no_changes_performed"),
            components=Button(
                id="gn_currency_view",
                owner_id=context.author_id,
                text=self.__i18n.get("extensions.general.remove_currency_workflow.view_currencies_button")
            ),
            embed=None
        )
