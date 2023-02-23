from collections.abc import Awaitable

from holobot.discord.sdk.events import CommandProcessedEvent
from holobot.discord.sdk.workflows.interactables import Command
from holobot.extensions.general.enums import ReactionType
from holobot.extensions.general.managers import IMarriageManager
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.database.enums import IsolationLevel
from holobot.sdk.database.exceptions import SerializationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.resilience import AsyncRetryPolicy
from holobot.sdk.reactive import IListener
from holobot.sdk.utils.dict_utils import get_generic
from holobot.sdk.utils.timedelta_utils import ZERO_TIMEDELTA

_REACTION_TYPE_BY_COMMAND: dict[str, ReactionType] = {
    "hug": ReactionType.HUG,
    "kiss": ReactionType.KISS,
    "pat": ReactionType.PAT,
    "poke": ReactionType.POKE,
    "lick": ReactionType.LICK,
    "bite": ReactionType.BITE,
    "handhold": ReactionType.HANDHOLD,
    "cuddle": ReactionType.CUDDLE
}

@injectable(IListener[CommandProcessedEvent])
class UpdateMarriageOnReaction(IListener[CommandProcessedEvent]):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        marriage_manager: IMarriageManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(UpdateMarriageOnReaction)
        self.__marriage_manager = marriage_manager
        self.__unit_of_work_provider = unit_of_work_provider

    async def on_event(self, event: CommandProcessedEvent) -> None:
        if (
            not isinstance(event.interactable, Command)
            or not event.server_id
            or event.interactable.group_name != "react"
            or event.interactable.subgroup_name
            or event.interactable.name not in _REACTION_TYPE_BY_COMMAND
        ):
            return

        target_user_id = get_generic(event.arguments, int, "target")
        if not target_user_id:
            return

        # TODO If the marriage has leveled up, send a message to the channel.
        # Also, include any newly unlocked perks.
        try:
            await self.__try_add_reaction(
                event.server_id,
                event.user_id,
                str(target_user_id),
                _REACTION_TYPE_BY_COMMAND[event.interactable.name]
            )
        except SerializationError as error:
            # Ignored, because we're in an event handler.
            self.__logger.debug(
                "Failed to update marriage due to a serialization error",
                error,
                server_id=event.server_id,
                user_id=event.user_id,
                target_user_id=target_user_id
            )

    def __try_add_reaction(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str,
        reaction_type: ReactionType
    ) -> Awaitable[None]:
        async def try_add_reaction(_: None) -> None:
            async with (unit_of_work := await self.__unit_of_work_provider.create_new(IsolationLevel.SERIALIZABLE)):
                is_reaction_added = await self.__marriage_manager.try_add_reaction(
                    server_id,
                    user_id1=user_id1,
                    user_id2=user_id2,
                    reaction_type=reaction_type
                )
                if is_reaction_added:
                    unit_of_work.complete()

        retry_policy = AsyncRetryPolicy[None, None](3, ZERO_TIMEDELTA, (SerializationError,))
        return retry_policy.execute(try_add_reaction, None)
