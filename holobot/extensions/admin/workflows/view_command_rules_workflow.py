from typing import Any

from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout, Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.admin import CommandRuleManagerInterface
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewCommandRulesWorkflow(WorkflowBase):
    def __init__(
        self,
        command_manager: CommandRuleManagerInterface,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_manager = command_manager
        self.__i18n_provider = i18n_provider
        self.__log = logger_factory.create(ViewCommandRulesWorkflow)

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
        group: str | None = None,
        subgroup: str | None = None
    ) -> InteractionResponse:
        if not group and subgroup:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.admin.view_command_rules_workflow.subgroup_requires_group_error"
                ))
            )

        content, components = await self.__create_page_content(
            context.server_id,
            context.author_id,
            group,
            subgroup,
            0,
            DEFAULT_PAGE_SIZE
        )
        return InteractionResponse(action=ReplyAction(
            content=content,
            components=components
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
            return InteractionResponse(EditMessageAction(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            ))

        group = state.custom_data.get("group")
        subgroup = state.custom_data.get("subgroup")
        content, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            group,
            subgroup if group else None,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE
        )
        return InteractionResponse(
            EditMessageAction(
                content=content,
                components=components
            )
        )

    async def __create_page_content(
        self,
        server_id: str,
        user_id: str,
        group: str | None,
        subgroup: str | None,
        page_index: int,
        page_size: int
    ) -> tuple[str | Embed, ComponentBase | list[Layout]]:
        self.__log.trace("User requested command rule list page", user_id=user_id, page_index=page_index)
        result = await self.__command_manager.get_rules_by_server(server_id, page_index, page_size, group, subgroup)
        if not result.items:
            return (self.__i18n_provider.get(
                "extensions.admin.view_command_rules_workflow.no_command_rules_configured"
            ), [])

        content = Embed(
            title=self.__i18n_provider.get(
                "extensions.admin.view_command_rules_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.admin.view_command_rules_workflow.embed_description"
            ),
            color=0xeb7d00,
            fields=[EmbedField(
                name=self.__i18n_provider.get(
                    "extensions.admin.view_command_rules_workflow.embed_name_field",
                    { "rule_id": rule.identifier }
                ),
                value=rule.textify(),
                is_inline=False
            ) for rule in result.items]
        )

        component = Paginator(
            id="avrc_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return (content, component)
