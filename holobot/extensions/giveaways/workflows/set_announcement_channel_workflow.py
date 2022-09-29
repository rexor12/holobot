from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ForbiddenError, InvalidChannelError
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.utils import get_channel_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.giveaways.models import GiveawayOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SetAnnouncementChannelWorkflow(WorkflowBase):
    def __init__(
        self,
        channel_manager: IChannelManager,
        i18n_provider: II18nProvider,
        options: IOptions[GiveawayOptions]
    ) -> None:
        super().__init__()
        self.__channel_manager = channel_manager
        self.__i18n_provider = i18n_provider
        self.__options = options

    @command(
        name="announce",
        group_name="giveaway",
        description="Enables or disables announcement of new giveaways.",
        required_permissions=Permission.ADMINISTRATOR,
        options=(
            Option(
                name="channel",
                description=(
                    "The channel in which to announce giveaways."
                    " Omit it if you want to disable the feature."
                ),
                is_mandatory=False
            ),
        )
    )
    async def set_announcement_channel(
        self,
        context: ServerChatInteractionContext,
        channel: str | None = None
    ) -> InteractionResponse:
        options = self.__options.value
        if not SetAnnouncementChannelWorkflow.__is_feature_enabled(options):
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("feature_disabled_error"))
            )

        channel_id = None
        try:
            if channel:
                channel_id = get_channel_id(channel.strip())
                if not channel_id:
                    return InteractionResponse(
                        action=ReplyAction(content=self.__i18n_provider.get("channel_not_found_error"))
                    )

                await self.__channel_manager.unfollow_news_channel_for_all_channels(
                    context.server_id,
                    options.AnnouncementServerId,
                    options.AnnouncementChannelId
                )
                await self.__channel_manager.follow_news_channel(
                    context.server_id,
                    channel_id,
                    options.AnnouncementServerId,
                    options.AnnouncementChannelId
                )

            if not channel_id:
                await self.__channel_manager.unfollow_news_channel_for_all_channels(
                    context.server_id,
                    options.AnnouncementServerId,
                    options.AnnouncementChannelId
                )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.giveaways.set_announcement_channel_workflow.forbidden_error"
                    )
                )
            )
        except InvalidChannelError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.giveaways.set_announcement_channel_workflow.invalid_channel_error"
                    )
                )
            )

        return InteractionResponse(
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.giveaways.set_announcement_channel_workflow.channel_set"
                    if channel_id
                    else "extensions.giveaways.set_announcement_channel_workflow.channel_unset",
                    { "channel_id": channel_id }
                )
            )
        )

    @staticmethod
    def __is_feature_enabled(options: GiveawayOptions) -> bool:
        return (
            not not options.AnnouncementServerId
            and options.AnnouncementServerId != "0"
            and not not options.AnnouncementChannelId
            and options.AnnouncementChannelId != "0"
        )
