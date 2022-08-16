from datetime import datetime
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.giveaways.events.models import NewGiveawaysEvent
from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener

@injectable(IListener[NewGiveawaysEvent])
@injectable(IWorkflow)
class PublishNewGiveawaysEventListener(WorkflowBase, IListener[NewGiveawaysEvent]):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        i18n_provider: II18nProvider,
        messaging: IMessaging
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__messaging = messaging
        self.__server_id = str(configurator.get("Giveaways", "GiveawayAnnouncementServerId", 0))
        self.__channel_id = str(configurator.get("Giveaways", "GiveawayAnnouncementChannelId", 0))
        self.__is_enabled = self.__is_feature_enabled()

    @command(
        name="gannounce",
        description="Test command."
    )
    async def dummy(self, context) -> InteractionResponse:
        await self.on_event(NewGiveawaysEvent(
            giveaways=(
                ExternalGiveawayItem(
                    0, datetime.utcnow(), None, datetime.utcnow(), "Steam", "game", "", "", "Ys VIII: Lacrimosa of Dana"
                ),
                ExternalGiveawayItem(
                    0, datetime.utcnow(), None, datetime.utcnow(), "Epic Games Store", "game", "", "", "Cook, Serve, Delicious! 3?!"
                ),
                ExternalGiveawayItem(
                    0, datetime.utcnow(), None, datetime.utcnow(), "Epic Games Store", "game", "", "", "Supraland"
                ),
                ExternalGiveawayItem(
                    0, datetime.utcnow(), None, datetime.utcnow(), "Epic Games Store", "game", "", "", "A Game Of Thrones: The Board Game Digital Edition"
                ),
                ExternalGiveawayItem(
                    0, datetime.utcnow(), None, datetime.utcnow(), "Steam", "game", "", "", "ARK: Survival Evolved"
                ),
            )
        ))
        return InteractionResponse(action=ReplyAction(content="ok"))

    async def on_event(self, event: NewGiveawaysEvent) -> None:
        if not self.__is_enabled:
            return

        items_i18n = self.__i18n_provider.get_list_items(
            "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost_list_item",
            [
                {
                    "title": giveaway.title,
                    "source": giveaway.source_name
                }
                for giveaway in event.giveaways
            ]
        )
        message_id = await self.__messaging.send_channel_message(
            self.__server_id,
            self.__channel_id,
            self.__i18n_provider.get(
                "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost",
                {
                    "items": "\n".join(items_i18n)
                }
            )
        )
        await self.__messaging.crosspost_message(self.__server_id, self.__channel_id, message_id)

    def __is_feature_enabled(self) -> bool:
        return (
            not not self.__server_id
            and self.__server_id != "0"
            and not not self.__channel_id
            and self.__channel_id != "0"
        )
