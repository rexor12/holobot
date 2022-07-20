from .. import CommandRuleManagerInterface
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Optional, Union

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewCommandRulesWorkflow(WorkflowBase):
    def __init__(self, command_manager: CommandRuleManagerInterface, log: LogInterface) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_manager: CommandRuleManagerInterface = command_manager
        self.__log: LogInterface = log.with_name("Admin", "ViewCommandRulesWorkflow")

    @command(
        description="Lists the rules set on this server.",
        name="viewrules",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("group", "The name of the command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The name of the command sub-group, such as \"commands\" under \"admin\".", is_mandatory=False)
        )
    )
    async def view_command_rules(
        self,
        context: ServerChatInteractionContext,
        group: Optional[str] = None,
        subgroup: Optional[str] = None
    ) -> InteractionResponse:
        if not group and subgroup:
            return InteractionResponse(
                action=ReplyAction(content="You can specify a subgroup if and only if you specify a group, too.")
            )

        return InteractionResponse(ReplyAction(
            await self.__create_page_content(
                context.server_id,
                context.author_id,
                group,
                subgroup,
                0,
                DEFAULT_PAGE_SIZE
            ),
            Paginator("avrc_paginator", current_page=0)
        ))

    @component(
        identifier="avrc_paginator",
        component_type=Paginator,
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not isinstance(state, PagerState)
        ):
            return InteractionResponse(EditMessageAction("An internal error occurred while processing the interaction."))

        group = state.custom_data.get("group")
        subgroup = state.custom_data.get("subgroup")
        return InteractionResponse(
            EditMessageAction(
                await self.__create_page_content(
                    context.server_id,
                    context.author_id,
                    group,
                    subgroup if group else None,
                    max(state.current_page, 0),
                    DEFAULT_PAGE_SIZE
                ),
                Paginator("avrc_paginator", current_page=max(state.current_page, 0))
            )
        )

    async def __create_page_content(
        self,
        server_id: str,
        user_id: str,
        group: Optional[str],
        subgroup: Optional[str],
        page_index: int,
        page_size: int
    ) -> Union[str, Embed]:
        self.__log.trace(f"User requested command rule list page. {{ UserId = {user_id}, Page = {page_index} }}")
        start_offset = page_index * page_size
        items = await self.__command_manager.get_rules_by_server(server_id, start_offset, page_size, group, subgroup)
        if len(items) == 0:
            return "No command rules matching the query have been configured for the server."

        return Embed(
            title="Command rules",
            description="The list of command rules set on this server.",
            color=0xeb7d00,
            fields=[EmbedField(
                name=f"Rule #{rule.id}",
                value=rule.textify(),
                is_inline=False
            ) for rule in items]
        )
