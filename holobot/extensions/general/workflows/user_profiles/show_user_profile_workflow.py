from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables.components import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.factories import IUserProfileFactory
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.caching import IObjectCache
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network import IHttpClientPool
from .user_profile_workflow_base import UserProfileWorkflowBase

@injectable(IWorkflow)
class ShowUserProfileWorkflow(UserProfileWorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        http_client_pool: IHttpClientPool,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        user_data_provider: IUserDataProvider,
        user_profile_factory: IUserProfileFactory,
        user_profile_repository: IUserProfileRepository
    ) -> None:
        super().__init__(
            cache,
            http_client_pool,
            user_data_provider,
            user_profile_factory
        )
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
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
        image_or_error = await self.__get_user_profile_image(
            context,
            str(user) if user else None
        )

        if isinstance(image_or_error, str):
            return self._reply(content=image_or_error)

        return self._reply(attachments=(image_or_error,))

    @component(identifier="vprofile")
    async def set_user_profile_badge(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (user_id := state.custom_data.get("u")) is None:
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        image_or_error = await self.__get_user_profile_image(context, user_id)
        if isinstance(image_or_error, str):
            return self._edit_message(content=image_or_error, embed=None, components=None)

        return self._edit_message(content=None, embed=None, components=None, attachments=(image_or_error,))

    async def __get_user_profile_image(
        self,
        context: InteractionContext,
        user_id: str | None
    ) -> bytes | str:
        if isinstance(context, ServerChatInteractionContext):
            target_user_id = user_id if user_id else context.author_id
            if not await self.__member_data_provider.is_member(context.server_id, target_user_id):
                return self.__i18n.get("extensions.general.show_user_profile_workflow.not_a_member_error")
        else:
            target_user_id = context.author_id

        if not (user_profile := await self.__user_profile_repository.get(target_user_id)):
            return self.__i18n.get("extensions.general.show_user_profile_workflow.profile_not_found_error")

        user_profile_image = await self._generate_user_profile(
            target_user_id,
            user_profile
        )

        return user_profile_image
