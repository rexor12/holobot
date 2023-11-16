from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import PaginatorState
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from .interactables.decorators import moderation_command, moderation_component

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewWarnStrikesWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        member_data_provider: IMemberDataProvider,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(ViewWarnStrikesWorkflow)
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__warn_manager: IWarnManager = warn_manager

    @moderation_command(
        description="Displays a user's warn strikes",
        name="view",
        group_name="moderation",
        subgroup_name="warns",
        options=(
            Option("user", "The user to inspect.", type=OptionType.USER),
        ),
        required_moderator_permissions=ModeratorPermission.WARN_USERS
    )
    async def view_warn_strikes(
        self,
        context: InteractionContext,
        user: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        user_id = str(user)
        if not await self.__member_data_provider.is_member(context.server_id, user_id):
            return self._reply(content="The user you mentioned cannot be found.")

        content, embed, components = await self.__create_page_content(
            context.server_id,
            user_id,
            0,
            DEFAULT_PAGE_SIZE,
            context.author_id
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @moderation_component(
        identifier="warn_paginator",
        is_bound=True,
        required_moderator_permissions=ModeratorPermission.WARN_USERS,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )
        if (user_id := state.custom_data.get("i", None)) is None:
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        content, embed, components = await self.__create_page_content(
            context.server_id,
            user_id,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE,
            context.author_id
        )

        return (
            self._edit_message(
                content=content,
                embed=embed,
                components=components
            )
            if isinstance(state, PaginatorState)
            else self._edit_message(content="An internal error occurred while processing the interaction.")
        )

    @moderation_component(
        identifier="remove_warn",
        is_bound=True,
        required_moderator_permissions=ModeratorPermission.WARN_USERS,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def remove_warn_strike(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )
        if (warn_strike_id := state.custom_data.get("i", None)) is None:
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        await self.__warn_manager.remove_warn(int(warn_strike_id))

        return self._edit_message(
            content=self.__i18n_provider.get(f"Warn strike #{warn_strike_id} has been removed."),
            embed=None,
            components=None
        )

    async def __create_page_content(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        page_size: int,
        owner_id: str
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        self.__logger.trace(
            "User requested warn strike page",
            server_id=server_id,
            user_id=user_id,
            page_index=page_index
        )
        result = await self.__warn_manager.get_warns(server_id, user_id, page_index, page_size)
        if not result.items:
            return ("The user has no warn strikes.", None, None)

        embed = Embed(
            title="Warn strikes",
            description=f"The list of warn strikes of <@{user_id}>."
        )

        remove_buttons = StackLayout(id="vwrmbtns")
        for warn_strike in result.items:
            embed.fields.append(EmbedField(
                name=f"Strike #{warn_strike.identifier}",
                value=(
                    f"> Reason: {warn_strike.reason}\n"
                    f"> Warned by <@{warn_strike.warner_id}> at {warn_strike.created_at:%I:%M:%S %p, %m/%d/%Y %Z}"
                ),
                is_inline=False
            ))
            remove_buttons.children.append(Button(
                id="remove_warn",
                owner_id=owner_id,
                text=f"🚮 #{warn_strike.identifier}",
                style=ComponentStyle.DANGER,
                custom_data={
                    "i": str(warn_strike.identifier),
                    "u": user_id
                }
            ))

        layouts = list[LayoutBase]()
        layouts.append(remove_buttons)
        layouts.append(Paginator(
            id="warn_paginator",
            owner_id=owner_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count,
            custom_data={"i": user_id}
        ))

        return (None, embed, layouts)
