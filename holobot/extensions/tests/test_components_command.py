from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.components import Button, ComboBox, ComboBoxItem, Paginator, StackLayout
from holobot.discord.sdk.components.enums import ComponentStyle
from holobot.discord.sdk.components.models import ComboBoxState, ComponentInteractionResponse, ComponentRegistration, PagerState
from holobot.discord.sdk.models import InteractionContext
from holobot.sdk.ioc.decorators import injectable
from typing import Any

@injectable(CommandInterface)
class TestComponentsCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("components")
        self.group_name = "tests"
        self.description = "Component test command."
        self.components = [
            ComponentRegistration("test_primary_button", Button, self.__on_test_button),
            ComponentRegistration("test_disabled_button", Button, self.__on_test_button),
            ComponentRegistration("test_combo_box", ComboBox, self.__on_test_combo_box),
            ComponentRegistration("test_paginator", Paginator, self.__on_test_paginator, DeferType.DEFER_MESSAGE_UPDATE)
        ]

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        return CommandResponse(
            ReplyAction(
                "Hello, World!",
                [
                    StackLayout(
                        "container1",
                        [
                            ComboBox(
                                "test_combo_box",
                                [
                                    ComboBoxItem("Option 1", "1", "Description 1"),
                                    ComboBoxItem("Option 2", "2", "Description 2"),
                                    ComboBoxItem("Option 3", "3", "Description 3")
                                ],
                                "Placeholder text",
                                1,
                                2,
                                True
                            )
                        ]
                    ),
                    StackLayout(
                        "container2",
                        [
                            Button("test_primary_button", "Click me!", ComponentStyle.PRIMARY, True),
                            Button("test_disabled_button", "Nope", ComponentStyle.SECONDARY, False)
                        ]
                    ),
                    Paginator("test_paginator", current_page=10)
                ]
            )
        )

    async def __on_test_button(
        self,
        registration: ComponentRegistration,
        context: InteractionContext,
        state: Any
    ) -> ComponentInteractionResponse:
        return ComponentInteractionResponse(
            ReplyAction(f"You've clicked {registration.id}.")
        )

    async def __on_test_combo_box(
        self,
        registration: ComponentRegistration,
        context: InteractionContext,
        state: Any
    ) -> ComponentInteractionResponse:
        return ComponentInteractionResponse(
            ReplyAction(f"You've selected {state.selected_values} in {registration.id}.")
            if isinstance(state, ComboBoxState)
            else ReplyAction(f"Wrong state type: {type(state)}")
        )

    async def __on_test_paginator(
        self,
        registration: ComponentRegistration,
        context: InteractionContext,
        state: Any
    ) -> ComponentInteractionResponse:
        return ComponentInteractionResponse(
            EditMessageAction(
                f"You've navigated to page {state.current_page} in {registration.id}.",
                Paginator("test_paginator", current_page=max(state.current_page, 0))
            )
            if isinstance(state, PagerState)
            else EditMessageAction(f"Wrong state type: {type(state)}")
        )
