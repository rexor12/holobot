from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.models import Embed, EmbedFooter
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.extensions.giveaways.events.models import NewGiveawaysEvent
from holobot.extensions.giveaways.models import GiveawayOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener

@injectable(IListener[NewGiveawaysEvent])
class PublishNewGiveawaysEventListener(IListener[NewGiveawaysEvent]):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        messaging: IMessaging,
        options: IOptions[GiveawayOptions],
        server_data_provider: IServerDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__messaging = messaging
        self.__options = options
        self.__server_data_provider = server_data_provider
        self.__is_enabled = self.__is_feature_enabled()

    async def on_event(self, event: NewGiveawaysEvent) -> None:
        if not self.__is_enabled:
            return

        items_i18n = self.__i18n_provider.get_list_items(
            "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost_list_item",
            [
                {
                    "title": giveaway.title,
                    "source": giveaway.source_name,
                    "url": giveaway.url
                }
                for giveaway in event.giveaways
            ]
        )

        options = self.__options.value
        try:
            message_id = await self.__messaging.send_channel_message(
                options.AnnouncementServerId,
                options.AnnouncementChannelId,
                Embed(
                    title=self.__i18n_provider.get(
                        "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost_header"
                    ),
                    description=self.__i18n_provider.get(
                        "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost",
                        {
                            "items": "\n".join(items_i18n)
                        }
                    ),
                    thumbnail_url=self.__options.value.GiveawayEmbedThumbnailUrl,
                    footer=EmbedFooter(
                        text=self.__i18n_provider.get(
                            "extensions.giveaways.publish_new_giveaways_event_listener.new_giveaways_crosspost_footer"
                        )
                    )
                ),
                suppress_user_mentions=True
            )
            await self.__messaging.crosspost_message(
                options.AnnouncementServerId,
                options.AnnouncementChannelId,
                message_id
            )
        except ForbiddenError:
            await self.__try_notify_admin_on_error()

    def __is_feature_enabled(self) -> bool:
        options = self.__options.value
        return (
            not not options.AnnouncementServerId
            and options.AnnouncementServerId != "0"
            and not not options.AnnouncementChannelId
            and options.AnnouncementChannelId != "0"
        )

    async def __try_notify_admin_on_error(self) -> None:
        options = self.__options.value
        try:
            server_data = await self.__server_data_provider.get_basic_data_by_id(
                options.AnnouncementServerId
            )
            await self.__messaging.send_private_message(
                server_data.owner_id,
                self.__i18n_provider.get(
                    "extensions.giveaways.publish_new_giveaways_event_listener.cannot_announce_error",
                    {
                        "channel_id": options.AnnouncementChannelId,
                        "server_name": server_data.name
                    }
                )
            )
        except ForbiddenError:
            # Tried our best, but we can't even send a message to the server administrator.
            pass
