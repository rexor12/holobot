from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button, StackLayout
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.exceptions import NotMarriedError
from holobot.extensions.general.managers import IMarriageManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class DivorceWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        marriage_manager: IMarriageManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__marriage_manager = marriage_manager

    @command(
        name="divorce",
        description="Get divorced from your beloved.",
        cooldown=Cooldown(
            duration=60,
            message="extensions.general.divorce_workflow.cooldown_error"
        )
    )
    async def divorce(self, context: InteractionContext) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        if not (spouse_id := await self.__marriage_manager.get_spouse_id(context.server_id, context.author_id)):
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.general.divorce_workflow.not_married_error"
                )
            )

        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.general.divorce_workflow.confirm_divorce",
                { "spouse_id": spouse_id }
            ),
            components=StackLayout(
                id="divorce_layout",
                children=[
                    Button(
                        id="divorce_yes",
                        owner_id=context.author_id,
                        text=self.__i18n_provider.get("common.buttons.yes"),
                        custom_data={ "uid": str(spouse_id) }
                    ),
                    Button(
                        id="divorce_no",
                        owner_id=context.author_id,
                        text=self.__i18n_provider.get("common.buttons.no"),
                        style=ComponentStyle.SECONDARY,
                        custom_data={ "uid": str(spouse_id) }
                    ),
                ]
            ),
            suppress_user_mentions=True
        )

    @component(
        identifier="divorce_yes",
        is_bound=True
    )
    async def confirm_divorce(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (spouse_id := get_custom_int(state.custom_data, "uid", None))
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        try:
            await self.__marriage_manager.divorce(context.server_id, context.author_id, spouse_id)
        except NotMarriedError:
            return self._edit_message(
                content=self.__i18n_provider.get(
                    "extensions.general.divorce_workflow.not_married_error"
                )
            )

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.divorce_workflow.got_divorced",
                {
                    "user_id": context.author_id,
                    "spouse_id": spouse_id
                }
            )
        )

    @component(
        identifier="divorce_no",
        is_bound=True
    )
    async def cancel_divorce(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not state.custom_data.get("uid", None)
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.divorce_workflow.divorce_canceled"
            )
        )
