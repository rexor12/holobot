
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, EmbedFooter
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_GLOBAL_AVATAR_VALUE = "global"
_SERVER_AVATAR_VALUE = "server"

@injectable(IWorkflow)
class ViewUserAvatarWorkflow(WorkflowBase):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        bot_data_provider: IBotDataProvider,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider
    ) -> None:
        super().__init__()
        self.__bot_data_provider = bot_data_provider
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__avatar_artwork_artist_name = configurator.get("General", "AvatarArtworkArtistName", "unknown")

    @command(
        description="Displays a user's avatar.",
        name="avatar",
        options=(
            Option(
                "user",
                "The name or mention of the user. By default, it's yourself.",
                is_mandatory=False
            ),
            Option(
                "kind",
                "Whether to show the global or the server-specific avatar.",
                OptionType.STRING,
                is_mandatory=False,
                choices=(
                    Choice("Global", _GLOBAL_AVATAR_VALUE),
                    Choice("Server", _SERVER_AVATAR_VALUE)
                )
            )
        )
    )
    async def view_user_avatar(
        self,
        context: ServerChatInteractionContext,
        user: str | None = None,
        kind: str | None = None
    ) -> InteractionResponse:
        try:
            if user is None:
                member = await self.__member_data_provider.get_basic_data_by_id(
                    context.server_id,
                    context.author_id
                )
            elif (user_id := get_user_id(user)) is not None:
                member = await self.__member_data_provider.get_basic_data_by_id(
                    context.server_id,
                    user_id
                )
            else:
                member = await self.__member_data_provider.get_basic_data_by_name(
                    context.server_id,
                    user.strip()
                )
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

        avatar_url = None
        no_avatar_i18n = None
        if not kind:
            avatar_url = member.server_specific_avatar_url or member.avatar_url
            if not avatar_url:
                no_avatar_i18n = "extensions.general.view_user_avatar_workflow.no_avatar_error"
        elif kind == _SERVER_AVATAR_VALUE:
            avatar_url = member.server_specific_avatar_url
            if not avatar_url:
                no_avatar_i18n = "extensions.general.view_user_avatar_workflow.no_server_avatar_error"
        else:
            avatar_url = member.avatar_url
            if not avatar_url:
                no_avatar_i18n = "extensions.general.view_user_avatar_workflow.no_global_avatar_error"

        if no_avatar_i18n:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        no_avatar_i18n,
                        { "user_id": member.user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        if member.user_id == self.__bot_data_provider.get_user_id():
            footer = EmbedFooter(
                text=self.__i18n_provider.get(
                    "extensions.general.view_user_avatar_workflow.embed_footer",
                    { "artist": self.__avatar_artwork_artist_name }
                )
            )
        else:
            footer = None

        return InteractionResponse(
            action=ReplyAction(content=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.view_user_avatar_workflow.embed_title",
                    { "user": member.display_name }
                ),
                image_url=avatar_url,
                footer=footer
            ))
        )
