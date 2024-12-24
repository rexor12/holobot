from collections.abc import Sequence
from typing import cast

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.models.embed import Embed
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComboBox, ComboBoxItem, ComboBoxState, LayoutBase, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.extensions.general.factories import IUserProfileFactory
from holobot.extensions.general.models.items import BackgroundItem
from holobot.extensions.general.models.user_profiles import UserProfileBackground
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.repositories import IUserItemRepository
from holobot.extensions.general.repositories.user_profiles import (
    IUserProfileBackgroundRepository, IUserProfileRepository
)
from holobot.sdk.caching import IObjectCache
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network import IHttpClientPool
from .user_profile_workflow_base import UserProfileWorkflowBase

_PAGE_SIZE: int = 10

@injectable(IWorkflow)
class ViewProfileBackgroundsWorkflow(UserProfileWorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        http_client_pool: IHttpClientPool,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reputation_data_provider: IReputationDataProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_data_provider: IUserDataProvider,
        user_item_repository: IUserItemRepository,
        user_profile_factory: IUserProfileFactory,
        user_profile_repository: IUserProfileRepository,
        user_profile_background_repository: IUserProfileBackgroundRepository
    ) -> None:
        super().__init__(
            cache,
            http_client_pool,
            user_data_provider,
            user_profile_factory
        )
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(ViewProfileBackgroundsWorkflow)
        self.__reputation_data_provider = reputation_data_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_item_repository = user_item_repository
        self.__user_profile_repository = user_profile_repository
        self.__user_profile_background_repository = user_profile_background_repository

    @command(
        group_name="profile",
        subgroup_name="background",
        name="view",
        description="View your profile with a specific background.",
        is_ephemeral=True,
        cooldown=Cooldown(duration=10),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def view_profile_backgrounds(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, embed, components = await self.__get_content_view_by_first_background(
            context.author_id
        )

        return self._reply(
            content=content,
            embed=embed,
            components=components
        )

    @component(identifier="uprofilebg", is_bound=True)
    async def view_profile_background(
        self,
        context: InteractionContext,
        state: ComboBoxState
    ) -> InteractionResponse:
        page_index, code = state.selected_values[0].split(";")
        content, embed, components = await self.__get_content_view_by_code(
            context.author_id,
            int(page_index),
            code
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(identifier="upsetbg", is_bound=True)
    async def set_profile_background(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if not (code := state.custom_data.get("c", None)):
            return self._edit_message(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None,
                attachments=None
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            background = await self.__user_profile_background_repository.get_by_code(code)
            is_unlocked = (
                await self.__user_item_repository.background_exists(
                    state.owner_id,
                    background.identifier
                )
                if background
                else False
            )
            if not background or not is_unlocked:
                return self._edit_message(
                    content=self.__i18n.get(
                        "extensions.general.view_profile_backgrounds_workflow.background_locked_error"
                    ),
                    embed=None,
                    components=None,
                    attachments=None
                )

            if not (user_profile := await self.__user_profile_repository.get(state.owner_id)):
                return self._edit_message(
                    content=self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.profile_not_found_error"),
                    embed=None,
                    components=None,
                    attachments=None
                )

            user_profile.background_image_id = background.identifier
            await self.__user_profile_repository.update(user_profile)

            unit_of_work.complete()

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.view_profile_backgrounds_workflow.updated_successfully",
                {
                    "background_name": background.name
                }
            ),
            embed=None,
            components=None,
            attachments=None
        )

    async def __get_content_view_by_first_background(
        self,
        user_id: int
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        user_items = await self.__user_item_repository.paginate_backgrounds(user_id, 0, 1)
        if not user_items.items:
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.no_available_backgrounds_error"),
                None,
                None
            )

        user_item = user_items.items[0]
        background_item = cast(BackgroundItem, user_item.item)
        background = await self.__user_profile_background_repository.get(
            background_item.background_id
        )
        if not background:
            self.__logger.error(
                "Found an invalid background-type user item",
                user_id=user_id,
                user_item_id=user_item.identifier,
                background_id=background_item.background_id
            )
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.invalid_background_error"),
                None,
                None
            )

        return await self.__get_content_view_by_custom_background(
            user_id,
            0,
            background
        )

    async def __get_content_view_by_code(
        self,
        user_id: int,
        page_index: int,
        code: str
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        background = await self.__user_profile_background_repository.get_by_code(code)
        if not background:
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.no_available_backgrounds_error"),
                None,
                None
            )

        return await self.__get_content_view_by_custom_background(user_id, page_index, background)

    async def __get_content_view_by_custom_background(
        self,
        user_id: int,
        page_index: int,
        background: UserProfileBackground
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        if not (user_profile := await self.__user_profile_repository.get(user_id)):
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.profile_not_found_error"),
                None,
                None
            )

        owned_background_infos = await self.__user_item_repository.paginate_background_infos(
            user_id,
            page_index,
            _PAGE_SIZE
        )

        embed = Embed(
            title=self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.general.view_profile_backgrounds_workflow.embed_description",
                {
                    "name": background.name
                }
            ),
            image_attachment=await self._generate_user_profile(
                user_id,
                user_profile,
                background.code
            )
        )

        comboBox = StackLayout(
            id="dummy",
            children=[
                ComboBox(
                    id="uprofilebg",
                    owner_id=user_id,
                    items=[
                        ComboBoxItem(text=item.name, value=f"{page_index};{item.code}")
                        for item in owned_background_infos.items
                    ]
                )
            ]
        )

        buttons = StackLayout(
            id="dummy",
            children=[
                Button(
                    id="upsetbg",
                    owner_id=user_id,
                    text=self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.apply_background_button"),
                    custom_data={"c": background.code}
                )
            ]
        )

        return (
            None,
            embed,
            [comboBox, buttons]
        )
