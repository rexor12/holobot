from datetime import datetime, time, timedelta, timezone

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.managers.user_profiles import IUserProfileManager
from holobot.extensions.general.models.user_profiles import ReputationCooldown
from holobot.extensions.general.repositories.user_profiles import (
    IReputationCooldownRepository, IUserProfileBackgroundRepository
)
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

_MIDNIGHT = time(hour=0, minute=0, tzinfo=timezone.utc)

@injectable(IWorkflow)
class GiveReputationPointWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        reputation_cooldown_repository: IReputationCooldownRepository,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_profile_background_repository: IUserProfileBackgroundRepository,
        user_profile_manager: IUserProfileManager
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__reputation_cooldown_repository = reputation_cooldown_repository
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_profile_background_repository = user_profile_background_repository
        self.__user_profile_manager = user_profile_manager

    @command(
        group_name="reputation",
        name="give",
        description="Gives a reputation point to a specific user.",
        cooldown=Cooldown(duration=5),
        options=(
            Option("user", "The user you'd like to give a reputation point to.", OptionType.USER),
        )
    )
    async def give_reputation_point(
        self,
        context: InteractionContext,
        user: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        source_user_id = context.author_id
        target_user_id = user
        if target_user_id == source_user_id:
            return self._reply(
                content=self.__i18n.get("extensions.general.give_reputation_point_workflow.cannot_choose_self_error")
            )

        if not await self.__member_data_provider.is_member(context.server_id, target_user_id):
            return self._reply(
                content=self.__i18n.get("extensions.general.give_reputation_point_workflow.not_a_member_error")
            )

        now = utcnow()
        reset_at = datetime.combine(now.date() + timedelta(days=1), _MIDNIGHT)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            cooldown = await self.__reputation_cooldown_repository.get(source_user_id)
            if cooldown and cooldown.last_rep_at.date() >= now.date():
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.give_reputation_point_workflow.cooldown_error",
                        {
                            "last_user_id": cooldown.last_target_user_id,
                            "reset_at": int(reset_at.timestamp())
                        }
                    ),
                    suppress_user_mentions=True
                )
            elif cooldown:
                cooldown.last_rep_at = now
                cooldown.last_target_user_id = target_user_id
                await self.__reputation_cooldown_repository.update(cooldown)
            else:
                cooldown = ReputationCooldown(
                    identifier=source_user_id,
                    last_target_user_id=target_user_id,
                    last_rep_at=now
                )
                await self.__reputation_cooldown_repository.add(cooldown)

            change_info = await self.__user_profile_manager.add_reputation_point(target_user_id)
            unit_of_work.complete()

        last_custom_background = change_info.last_custom_background
        if (
            not last_custom_background
            or last_custom_background.required_reputation < change_info.reputation_points
        ):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.give_reputation_point_workflow.reputation_given_successfully",
                    {
                        "target_user_id": target_user_id
                    }
                )
            )

        background_name = await self.__user_profile_background_repository.get_name_by_code(
            last_custom_background.code
        )

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.give_reputation_point_workflow.reputation_given_successfully_with_unlock",
                {
                    "target_user_id": target_user_id,
                    "custom_background_name": background_name
                }
            )
        )
