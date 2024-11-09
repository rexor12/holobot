from collections.abc import Awaitable

from holobot.discord.sdk.exceptions import ServerNotFoundError
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button, StackLayout
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.exceptions import AlreadyMarriedError, NotMarriedError
from holobot.extensions.general.managers import IMarriageManager
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.database.enums import IsolationLevel
from holobot.sdk.database.exceptions import SerializationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience import AsyncRetryPolicy
from holobot.sdk.utils.timedelta_utils import ZERO_TIMEDELTA

@injectable(IWorkflow)
class MarryWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        marriage_manager: IMarriageManager,
        member_data_provider: IMemberDataProvider,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__marriage_manager = marriage_manager
        self.__member_data_provider = member_data_provider
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        name="marry",
        description="Get married to someone.",
        options=(
            Option("user", "The user to get married to.", OptionType.USER),
        ),
        cooldown=Cooldown(
            duration=60,
            message="extensions.general.marry_workflow.cooldown_error"
        )
    )
    async def request_marriage(
        self,
        context: InteractionContext,
        user: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        target_user_id = user
        if target_user_id == context.author_id:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.general.marry_workflow.cannot_marry_self"
                )
            )

        if spouse_id := await self.__marriage_manager.get_spouse_id(context.server_id, context.author_id):
            return (
                self.__get_renew_response(context.author_id, spouse_id)
                if spouse_id == target_user_id
                else self.__get_self_already_married_response(context.author_id, spouse_id)
            )

        if spouse_id := await self.__marriage_manager.get_spouse_id(context.server_id, target_user_id):
            return self.__get_other_already_married_response(target_user_id, spouse_id)

        try:
            if not await self.__member_data_provider.is_member(context.server_id, target_user_id):
                return self._reply(content=self.__i18n_provider.get("user_not_found_error"))
        except ServerNotFoundError:
            return self._reply(content=self.__i18n_provider.get("server_not_found_error"))

        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.confirm_marry",
                {
                    "user_id": context.author_id,
                    "spouse_id": target_user_id
                }
            ),
            components=StackLayout(
                id="marry_layout",
                children=[
                    Button(
                        id="marry_yes",
                        owner_id=target_user_id,
                        text=self.__i18n_provider.get(
                            "extensions.general.marry_workflow.confirm_yes"
                        ),
                        custom_data={
                            "uid": str(context.author_id)
                        }
                    ),
                    Button(
                        id="marry_no",
                        owner_id=target_user_id,
                        text=self.__i18n_provider.get(
                            "extensions.general.marry_workflow.confirm_no"
                        ),
                        style=ComponentStyle.SECONDARY,
                        custom_data={
                            "uid": str(context.author_id)
                        }
                    ),
                ]
            )
        )

    @component(
        identifier="marry_yes",
        is_bound=True
    )
    async def accept_marry_request(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := get_custom_int(state.custom_data, "uid", None))
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        try:
            await self.__try_marry(context.server_id, user_id, context.author_id)
        except AlreadyMarriedError as error:
            if error.user_id1 == context.author_id:
                return self.__get_self_already_married_response(error.user_id2, error.user_id1, True)
            return self.__get_other_already_married_response(error.user_id2, error.user_id1, True)

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.got_married",
                {
                    "user_id": user_id,
                    "spouse_id": context.author_id
                }
            )
        )

    @component(
        identifier="marry_no",
        is_bound=True
    )
    async def refuse_marry_request(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := state.custom_data.get("uid", None))
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.request_refused",
                {
                    "user_id": user_id,
                    "spouse_id": context.author_id
                }
            ),
            suppress_user_mentions=True
        )

    @component(
        identifier="remarry_yes",
        is_bound=True
    )
    async def accept_remarry_request(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := get_custom_int(state.custom_data, "uid", None))
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        spouse_id = await self.__marriage_manager.get_spouse_id(context.server_id, user_id)
        if spouse_id != context.author_id:
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.got_remarried",
                {
                    "user_id": user_id,
                    "spouse_id": context.author_id
                }
            )
        )

    @component(
        identifier="remarry_no",
        is_bound=True
    )
    async def refuse_remarry_request(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (user_id := get_custom_int(state.custom_data, "uid", None))
        ):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        try:
            await self.__marriage_manager.divorce(context.server_id, user_id, context.author_id)
        except NotMarriedError:
            return self._edit_message(
                content=self.__i18n_provider.get(
                    "extensions.general.marry_workflow.not_married_error"
                )
            )

        return self._edit_message(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.got_divorced",
                {
                    "user_id": user_id,
                    "spouse_id": context.author_id
                }
            )
        )

    def __try_marry(
        self,
        server_id: int,
        user_id1: int,
        user_id2: int
    ) -> Awaitable[None]:
        async def try_marry(_: None) -> None:
            async with (unit_of_work := await self.__unit_of_work_provider.create_new(IsolationLevel.SERIALIZABLE)):
                await self.__marriage_manager.marry(server_id, user_id1, user_id2)
                unit_of_work.complete()

        retry_policy = AsyncRetryPolicy[None, None](3, ZERO_TIMEDELTA, (SerializationError,))
        return retry_policy.execute(try_marry, None)

    def __get_already_married_response(
        self,
        user_id: int,
        spouse_id: int,
        localization_key: str,
        is_edit: bool
    ) -> InteractionResponse:
        content = self.__i18n_provider.get(
            localization_key,
            {
                "user_id": user_id,
                "spouse_id": spouse_id
            }
        )
        if is_edit:
            return self._edit_message(content=content, suppress_user_mentions=True)

        return self._reply(content=content, suppress_user_mentions=True)

    def __get_renew_response(
        self,
        user_id: int,
        spouse_id: int
    ) -> InteractionResponse:
        return self._reply(
            content=self.__i18n_provider.get(
                "extensions.general.marry_workflow.confirm_remarry",
                {
                    "user_id": user_id,
                    "spouse_id": spouse_id
                }
            ),
            components=StackLayout(
                id="remarry_layout",
                children=[
                    Button(
                        id="remarry_yes",
                        owner_id=spouse_id,
                        text=self.__i18n_provider.get(
                            "extensions.general.marry_workflow.confirm_yes"
                        ),
                        custom_data={
                            "uid": str(user_id)
                        }
                    ),
                    Button(
                        id="remarry_no",
                        owner_id=spouse_id,
                        text=self.__i18n_provider.get(
                            "extensions.general.marry_workflow.confirm_no"
                        ),
                        style=ComponentStyle.SECONDARY,
                        custom_data={
                            "uid": str(user_id)
                        }
                    ),
                ]
            )
        )

    def __get_self_already_married_response(
        self,
        user_id: int,
        spouse_id: int,
        is_edit: bool = False
    ) -> InteractionResponse:
        return self.__get_already_married_response(
            user_id,
            spouse_id,
            "extensions.general.marry_workflow.already_married",
            is_edit
        )

    def __get_other_already_married_response(
        self,
        user_id: int,
        spouse_id: int,
        is_edit: bool = False
    ) -> InteractionResponse:
        return self.__get_already_married_response(
            user_id,
            spouse_id,
            "extensions.general.marry_workflow.already_married_other",
            is_edit
        )
