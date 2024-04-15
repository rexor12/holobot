from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.models.embed import Embed
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComboBox, ComboBoxItem, ComboBoxState, LayoutBase, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.extensions.general.factories import IUserProfileFactory
from holobot.extensions.general.models.user_profiles import CustomBackgroundInfo
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.caching import IObjectCache
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network import IHttpClientPool
from .user_profile_workflow_base import UserProfileWorkflowBase

@injectable(IWorkflow)
class ViewProfileBackgroundsWorkflow(UserProfileWorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        http_client_pool: IHttpClientPool,
        i18n_provider: II18nProvider,
        reputation_data_provider: IReputationDataProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
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
        self.__reputation_data_provider = reputation_data_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_profile_repository = user_profile_repository

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
        content, embed, components = await self.__get_content_view_by_index(context.author_id, 0)

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
        content, embed, components = await self.__get_content_view_by_code(context.author_id, state.selected_values[0])

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
        if (
            not (code := state.custom_data.get("c", None))
            or not (custom_background := self.__reputation_data_provider.get_custom_background_by_code(code))
        ):
            return self._edit_message(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None,
                attachments=None
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            if not (user_profile := await self.__user_profile_repository.get(state.owner_id)):
                return self._edit_message(
                    content=self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.profile_not_found_error"),
                    embed=None,
                    components=None,
                    attachments=None
                )

            if user_profile.reputation_points < custom_background.required_reputation:
                return self._edit_message(
                    content=self.__i18n.get(
                        "extensions.general.view_profile_backgrounds_workflow.background_locked_error",
                        {
                            "required_points": custom_background.required_reputation - user_profile.reputation_points
                        }
                    ),
                    embed=None,
                    components=None,
                    attachments=None
                )

            user_profile.background_image_code = custom_background.code
            await self.__user_profile_repository.update(user_profile)

            unit_of_work.complete()

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.view_profile_backgrounds_workflow.updated_successfully",
                {
                    "background_name": self.__i18n.get(
                        f"extensions.general.custom_background_names.{custom_background.code}"
                    )
                }
            ),
            embed=None,
            components=None,
            attachments=None
        )

    async def __get_content_view_by_index(
        self,
        user_id: str,
        index: int
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        custom_background = self.__reputation_data_provider.get_custom_background(index)
        if not custom_background and index > 0:
            index = 0
            custom_background = self.__reputation_data_provider.get_custom_background(index)
        if not custom_background:
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.no_available_backgrounds_error"),
                None,
                None
            )

        return await self.__get_content_view_by_custom_background(user_id, custom_background)

    async def __get_content_view_by_code(
        self,
        user_id: str,
        code: str
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        custom_background = self.__reputation_data_provider.get_custom_background_by_code(code)
        if not custom_background:
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.no_available_backgrounds_error"),
                None,
                None
            )

        return await self.__get_content_view_by_custom_background(user_id, custom_background)

    async def __get_content_view_by_custom_background(
        self,
        user_id: str,
        custom_background: CustomBackgroundInfo
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        if not (user_profile := await self.__user_profile_repository.get(user_id)):
            return (
                self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.profile_not_found_error"),
                None,
                None
            )

        is_unlocked = user_profile.reputation_points >= custom_background.required_reputation

        embed = Embed(
            title=self.__i18n.get("extensions.general.view_profile_backgrounds_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.general.view_profile_backgrounds_workflow.embed_description",
                {
                    "code": custom_background.code,
                    "required_reputation": custom_background.required_reputation,
                    "is_unlocked": self.__i18n.get(
                        "common.labels.yes" if is_unlocked else "common.labels.no"
                    ),
                    "name": self.__i18n.get(
                        f"extensions.general.custom_background_names.{custom_background.code}"
                    )
                }
            ),
            image_attachment=await self._generate_user_profile(
                user_id,
                user_profile,
                custom_background.code
            )
        )

        comboBox = StackLayout(
            id="dummy",
            children=[
                ComboBox(
                    id="uprofilebg",
                    owner_id=user_id,
                    items=[
                        ComboBoxItem(
                            text=self.__i18n.get(f"extensions.general.custom_background_names.{item.code}"),
                            value=item.code
                        )
                        for item in self.__reputation_data_provider.get_custom_backgrounds()
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
                    is_enabled=is_unlocked,
                    custom_data={"c": custom_background.code}
                )
            ]
        )

        return (
            None,
            embed,
            [comboBox, buttons]
        )
