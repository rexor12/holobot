from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    InteractionResponse, Option, StringOption
)
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import (
    MUDADA_FEATURE_NAME, VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.repositories import ITransactionRepository
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

_MESSAGE_LENGTH_MAX: int = 120

@injectable(IWorkflow)
class SetGiftMessageWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        transaction_repository: ITransactionRepository,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__transaction_repository = transaction_repository
        self.__unit_of_work_provider = unit_of_work_provider

    @requires_event(VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="letter",
        description="Set the message for a gift.",
        options=(
            Option("user", "The user you're sending the gift to.", OptionType.USER),
            StringOption("message", "The message you'd like to send the user.", OptionType.STRING, max_length=_MESSAGE_LENGTH_MAX)
        ),
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        is_ephemeral=True
    )
    async def set_gift_message(
        self,
        context: InteractionContext,
        user: int,
        message: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        target_user_id = user
        if target_user_id == context.author_id:
            return self._reply(content=self.__i18n.get("extensions.mudada.set_gift_message_workflow.self_transfer_error"))

        if len(message) > _MESSAGE_LENGTH_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.set_gift_message_workflow.message_too_long_error",
                    {
                        "max_length": _MESSAGE_LENGTH_MAX
                    }
                )
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            transaction = await self.__transaction_repository.get_by_users(context.author_id, target_user_id)
            if not transaction:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.set_gift_message_workflow.missing_transaction_error",
                        {
                            "user_id": target_user_id
                        }
                    ),
                    suppress_user_mentions=True
                )

            transaction.message = message
            await self.__transaction_repository.update(transaction)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get("extensions.mudada.set_gift_message_workflow.message_updated_successfully")
        )
