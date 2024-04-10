from datetime import timedelta

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.factories import IUserProfileFactory
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.caching import AbsoluteExpirationCacheEntryPolicy, IObjectCache
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.utils.datetime_utils import utcnow

_EXPIRATION_TIME = timedelta(minutes=10)

@injectable(IWorkflow)
class ShowUserProfileWorkflow(WorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        http_client_pool: IHttpClientPool,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        user_data_provider: IUserDataProvider,
        user_profile_factory: IUserProfileFactory,
        user_profile_repository: IUserProfileRepository,
    ) -> None:
        super().__init__()
        self.__cache = cache
        self.__http_client_pool = http_client_pool
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__user_data_provider = user_data_provider
        self.__user_profile_factory = user_profile_factory
        self.__user_profile_repository = user_profile_repository

    @command(
        group_name="profile",
        name="view",
        description="Displays a user's profile or your own.",
        options=(
            Option("user", "The user you'd like to view.", OptionType.USER, False),
        ),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=5)
    )
    async def show_user_profile(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        if isinstance(context, ServerChatInteractionContext):
            target_user_id = str(user) if user else context.author_id
            if not await self.__member_data_provider.is_member(context.server_id, target_user_id):
                return self._reply(
                    content=self.__i18n.get("extensions.general.show_user_profile_workflow.not_a_member_error")
                )
        else:
            target_user_id = context.author_id

        if not (user_profile := await self.__user_profile_repository.get(target_user_id)):
            return self._reply(
                content=self.__i18n.get("extensions.general.show_user_profile_workflow.profile_not_found_error")
            )

        user_data = await self.__user_data_provider.get_user_data_by_id(target_user_id)
        avatar_bytes: bytes | None = None
        if user_data.avatar_url_small:
            avatar_url = user_data.avatar_url_small
            cached_avatar = await self.__cache.get_or_add(
                f"UserProfile/Avatar/{user_data.user_id}",
                lambda _: self.__http_client_pool.get_raw(avatar_url),
                AbsoluteExpirationCacheEntryPolicy(expires_at=utcnow() + _EXPIRATION_TIME)
            )
            if isinstance(cached_avatar, bytes):
                avatar_bytes = cached_avatar

        user_profile_image = self.__user_profile_factory.create_profile_image(user_data.name, user_profile, avatar_bytes)

        return self._reply(
            attachments=(user_profile_image,)
        )
