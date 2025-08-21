import datetime

from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.extensions.dev.constants import DEV_FEATURE_NAME
from holobot.extensions.giveaways.events.models import NewGiveawaysEvent
from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.chrono import IClock
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IWorkflow)
class AnnounceGiveawayTestWorkflow(WorkflowBase):
    def __init__(
        self,
        clock: IClock,
        listeners: tuple[IListener[NewGiveawaysEvent], ...],
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__clock = clock
        self.__listeners = listeners
        self.__logger = logger_factory.create(AnnounceGiveawayTestWorkflow)

    @command(
        group_name="dev",
        name="gwannounce",
        description="Send a test giveaway announcement.",
        required_permissions=Permission.ADMINISTRATOR,
        restrictions=(FeatureRestriction(feature_name=DEV_FEATURE_NAME),)
    )
    async def announce_giveaway(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        event = NewGiveawaysEvent(giveaways=(
            ExternalGiveawayItem(
                identifier=0,
                created_at=self.__clock.now_utc(),
                start_time=None,
                end_time=self.__clock.now_utc() + datetime.timedelta(days=2),
                source_name="Steam",
                item_type="game",
                url="https://store.steampowered.com/app/1065970/VRSpiceWolfVR/",
                preview_url=None,
                title="狼と香辛料VR/Spice&WolfVR"
            ),
            ExternalGiveawayItem(
                identifier=0,
                created_at=self.__clock.now_utc(),
                start_time=None,
                end_time=self.__clock.now_utc() + datetime.timedelta(days=3),
                source_name="Epic Games Store",
                item_type="game",
                url="https://store.epicgames.com/en-US/p/ender-lilies-quietus-of-the-knights-9cea76",
                preview_url=None,
                title="ENDER LILIES: Quietus of the Knights"
            ),
        ))
        for listener in self.__listeners:
            try:
                await listener.on_event(event)
            except Exception as error:
                self.__logger.error("Failed to execute listener", error, listener_type=type(listener).__name__)

        return self._reply(content="Ok", is_ephemeral=True)
