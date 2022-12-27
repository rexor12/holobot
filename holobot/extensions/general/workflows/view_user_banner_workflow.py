from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewUserBannerWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        user_data_provider: IUserDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__user_data_provider = user_data_provider

    @command(
        description="Displays a user's banner.",
        name="banner",
        options=(
            Option(
                "user",
                "The name or mention of the user. By default, it's yourself.",
                is_mandatory=False
            ),
        )
    )
    async def view_user_banner(
        self,
        context: ServerChatInteractionContext,
        user: str | None = None
    ) -> InteractionResponse:
        try:
            if user is None:
                user_data = await self.__user_data_provider.get_user_data_by_id(
                    context.author_id,
                    False
                )
            elif (user_id := get_user_id(user.strip())) is not None:
                user_data = await self.__user_data_provider.get_user_data_by_id(
                    user_id,
                    False
                )
            else:
                user_data = await self.__user_data_provider.get_user_data_by_name(
                    context.server_id,
                    user.strip(),
                    False
                )

            user_name = user_data.name
            if member := await self.__member_data_provider.get_basic_data_by_id(
                context.server_id, user_data.user_id
            ):
                user_name = member.display_name
        except UserNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("user_not_found_error")
            )
        except ServerNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("server_not_found_error")
            )
        except ChannelNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("channel_not_found_error")
            )

        if not user_data.banner_url:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.general.view_user_banner_workflow.no_banner_error",
                    { "user_id": user_data.user_id }
                ),
                suppress_user_mentions=True
            )

        return self._reply(
            embed=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.view_user_banner_workflow.embed_title",
                    { "user": user_name }
                ),
                image_url=user_data.banner_url
            )
        )
