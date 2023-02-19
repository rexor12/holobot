from typing import Any

from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComboBox, ComboBoxItem, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.models import ComboBoxState, PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

PAGE_SIZE = 10

@injectable(IWorkflow)
class ShowAvailableServersWorkflow(WorkflowBase):
    def __init__(
        self,
        bot_data_provider: IBotDataProvider,
        member_data_provider: IMemberDataProvider
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__bot_data_provider = bot_data_provider
        self.__member_data_provider = member_data_provider

    @command(
        description="Displays information about the servers the bot is in.",
        name="servers",
        group_name="dev",
        # TODO Provide development server ID dynamically. (#135)
        server_ids={"999259836439081030"}
    )
    async def show_available_servers(
        self,
        context: InteractionContext,
    ) -> InteractionResponse:
        content, embed, layout = await self.__create_page_content(0, PAGE_SIZE, 0, context.author_id)
        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=layout
        )

    @component(
        identifier="dev_avsrvp",
        component_type=Paginator
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, PagerState):
            return self._edit_message(content="This interaction isn't valid anymore.")

        content, embed, components = await self.__create_page_content(
            max(state.current_page, 0),
            PAGE_SIZE,
            0,
            state.owner_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="dev_avsrvcb",
        component_type=ComboBox
    )
    async def change_server(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ComboBoxState):
            return self._edit_message(content="This interaction isn't valid anymore.")

        page_index, server_index = state.selected_values[0].split(";")
        content, embed, components = await self.__create_page_content(
            max(int(page_index), 0),
            PAGE_SIZE,
            max(int(server_index), 0),
            state.owner_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __create_page_content(
        self,
        page_index: int,
        page_size: int,
        server_index: int,
        initiator_id: str
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        server_count, servers = self.__bot_data_provider.get_servers(page_index, page_size)
        if not servers:
            return ("The bot isn't part of any servers.", None, None)

        if server_index >= len(servers):
            return ("You selected an inexistent server.", None, None)

        server = servers[server_index]
        owner_name = server.owner_name
        owner = None
        if not owner_name and server.owner_id:
            owner = await self.__member_data_provider.get_basic_data_by_id(
                server.identifier,
                server.owner_id
            )
            owner_name = owner.name if owner else "N/A"

        return (
            None,
            Embed(
                title=server.name,
                thumbnail_url=server.icon_url,
                fields=[
                    EmbedField("Owner", f"{owner_name} ({server.owner_id})", is_inline=False),
                    EmbedField("Members", str(server.member_count) if server.member_count else "N/A", is_inline=False),
                    EmbedField("Size", "Large" if server.is_large == True else "Small" if server.is_large == False else "N/A", is_inline=False),
                    EmbedField("Joined at", f"{server.joined_at:%I:%M:%S %p, %m/%d/%Y} UTC" if server.joined_at else "N/A", is_inline=False),
                    EmbedField("Shard ID", str(server.shard_id) if server.shard_id is not None else "N/A", is_inline=False)
                ]
            ),
            [
                StackLayout(id="dev_avsrvs1", children=[
                    ComboBox(
                        id="dev_avsrvcb",
                        owner_id=initiator_id,
                        placeholder="Choose a server",
                        items=[
                            ComboBoxItem(text=server.name, value=f"{page_index};{index}")
                            for index, server in enumerate(servers)
                        ]
                    )
                ]),
                Paginator(
                    id="dev_avsrvp",
                    owner_id=initiator_id,
                    current_page=page_index,
                    page_size=page_size,
                    total_count=server_count
                )
            ]
        )
