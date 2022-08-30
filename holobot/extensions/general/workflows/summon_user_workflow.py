
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import DoNothingAction, ReplyAction
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ForbiddenError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.utils.mention_utils import get_channel_id_or_default
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

MESSAGE_LENGTH_MAX = 192

@injectable(IWorkflow)
class SummonUserWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        messaging: IMessaging
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__messaging = messaging

    @command(
        description="Requests a user's presence via a direct message.",
        name="summon",
        options=(
            Option("name", "The name or mention of the user.", OptionType.STRING, True),
            Option("message", "An optional message the bot forwards to the user.", OptionType.STRING, False),
            Option("channel", "An optional mention of the channel where the user should be summoned.", OptionType.STRING, False)
        ),
        cooldown=Cooldown(duration=10)
    )
    async def summon_user(
        self,
        context: ServerChatInteractionContext,
        name: str,
        message: str | None = None,
        channel: str | None = None
    ) -> InteractionResponse:
        if not name:
            return InteractionResponse(ReplyAction(content=self.__i18n_provider.get(
                "missing_required_argument_error", { "argname": "name" }
            )))

        try:
            name = name.strip()
            user_id = get_user_id(name)
            member = (
                await self.__member_data_provider.get_basic_data_by_id(context.server_id, user_id)
                if user_id
                else await self.__member_data_provider.get_basic_data_by_name(context.server_id, name)
            )
            if not member:
                return InteractionResponse(action=ReplyAction(
                    content=self.__i18n_provider.get("user_not_found_error")
                ))
            if member.is_self:
                return InteractionResponse(action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.general.summon_user_workflow.cannot_summon_self_error"
                    )
                ))
            if member.is_bot:
                return InteractionResponse(action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.general.summon_user_workflow.cannot_summon_bot_error"
                    )
                ))

            user_id = member.user_id
            if user_id == context.author_id:
                return InteractionResponse(ReplyAction(content=self.__i18n_provider.get(
                    "extensions.general.summon_user_workflow.self_summon",
                    { "user_id": context.author_id }
                )))

            channel_id = get_channel_id_or_default(channel, context.channel_id) if channel else context.channel_id
            dm_message_key = "extensions.general.summon_user_workflow.dm_summon"
            if message:
                message = message.strip()[:MESSAGE_LENGTH_MAX]
                dm_message_key = "extensions.general.summon_user_workflow.dm_summon_with_message"

            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    dm_message_key,
                    {
                        "user_name": context.author_nickname or context.author_name,
                        "channel_id": channel_id,
                        "message": message
                    }
                )
            )
        except ForbiddenError:
            return InteractionResponse(action=ReplyAction(
                content=self.__i18n_provider.get("missing_dm_permission_error")
            ))
        except UserNotFoundError:
            return InteractionResponse(ReplyAction(
                content=self.__i18n_provider.get("user_not_found_error")
            ))
        except ServerNotFoundError:
            return InteractionResponse(action=ReplyAction(
                content=self.__i18n_provider.get("server_not_found_error")
            ))
        except ChannelNotFoundError:
            return InteractionResponse(action=ReplyAction(
                content=self.__i18n_provider.get("channel_not_found_error")
            ))

        return InteractionResponse(action=ReplyAction(
            content=self.__i18n_provider.get(
                "extensions.general.summon_user_workflow.successful_summon",
                { "user_id": user_id }
            ),
            suppress_user_mentions=True
        ))
