from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, ContainerLayout, Label, SectionLayout, Separator,
    StackLayout, Thumbnail
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.general.providers import IReactionProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ComponentsV2Demo(WorkflowBase):
    def __init__(
        self,
        reaction_provider: IReactionProvider
    ) -> None:
        super().__init__()
        self.__reaction_provider = reaction_provider

    @command(
        name="componentsv2",
        description="Components V2 demo.",
        required_permissions=Permission.ADMINISTRATOR
    )
    async def execute(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        return self._reply(
            components=ContainerLayout(
                id="_",
                accent_color=2331321,
                is_spoiler=True,
                children=[
                    SectionLayout(
                        id="_1",
                        children=[
                            Label(id="_1_1", content="# Holo\n\n-# Level: 9 000\n-# Experience: 999/1 000\n-# Reputation: 1 000 000")
                        ],
                        accessory=Thumbnail(
                            id="_1_0",
                            media="https://cdn.discordapp.com/avatars/791766309611634698/eafedd554405010bcdf642cfb7a8fe9c.png?size=256",
                            description="Holo's sexy avatar"
                        )
                    ),
                    Separator(id="_3"),
                    SectionLayout(
                        id="_2",
                        children=[
                            Label(id="_2_1", content="**Adopted** <t:1750449720:R>"),
                            Label(id="_2_2", content="**Friendly to** <:SantaHomu:1178804279046312128> <:Sissily:1160870365476691988>"),
                            Label(id="_2_3", content="**Hostile to** <:Orclown:1131952792077078568>")
                        ],
                        accessory=Button(
                            id="_tc2details",
                            owner_id=context.author_id,
                            text="Details",
                            style=ComponentStyle.SECONDARY
                        )
                    ),
                    Separator(id="_4"),
                    StackLayout(
                        id="_5",
                        children=[
                            Button(
                                id="_tc2pat",
                                owner_id=context.author_id,
                                text="Pat"
                            ),
                            Button(
                                id="_tc2fire",
                                owner_id=context.author_id,
                                text="Abandon",
                                style=ComponentStyle.DANGER
                            )
                        ]
                    )
                ]
            )
        )

    @component(identifier="_tc2details", is_ephemeral=True)
    async def on_tc2(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._reply(content="There are no further details available right now.")

    @component(identifier="_tc2pat", is_ephemeral=False)
    async def on_tc2_pat(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._reply(
            content=await self.__reaction_provider.get("pat")
        )

    @component(identifier="_tc2fire", is_ephemeral=True)
    async def on_tc2_fire(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._reply(content="<:HoloPout:1107797451684986890>")
