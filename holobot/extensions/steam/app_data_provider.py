import asyncio
from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import cast

from suffix_tree import Tree

from holobot.sdk.caching import IObjectCache
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from .endpoints import ISteamAppsClient
from .iapp_data_provider import IAppDataProvider
from .models import SteamApp, SteamAppsOptions

@dataclass(kw_only=True, frozen=True)
class _AppData:
    apps: dict[int, SteamApp] = field(default_factory=dict)
    suffix_tree: Tree = field(default_factory=Tree)

@injectable(IStartable)
@injectable(IAppDataProvider)
class AppDataProvider(IAppDataProvider, IStartable):
    def __init__(
        self,
        cache: IObjectCache,
        api_client: ISteamAppsClient,
        logger_factory: ILoggerFactory,
        options: IOptions[SteamAppsOptions]
    ) -> None:
        super().__init__()
        self.__api_client = api_client
        self.__cache = cache
        self.__logger = logger_factory.create(AppDataProvider)
        self.__options = options
        self.__token_source: CancellationTokenSource | None = None
        self.__background_task: Awaitable[None] | None = None
        self.__app_data = _AppData()

    async def start(self):
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__refresh_app_list(self.__token_source.token)
        )

    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass

    async def get(self, identifier: int) -> SteamApp | None:
        return self.__app_data.apps.get(identifier)

    async def find(self, name: str) -> SteamApp | None:
        # Copy reference to avoid concurrent change due to refreshes.
        app_data = self.__app_data
        matches = app_data.suffix_tree.find_all(name)
        return app_data.apps[cast(int, matches[0][0])] if matches else None

    async def __refresh_app_list(self, token: CancellationToken) -> None:
        await wait(self.__options.value.RefreshDelay, token)
        while not token.is_cancellation_requested:
            await wait(self.__options.value.RefreshResolution, token)
            continue

            # TODO This is super slow because of the suffix tree building.
            self.__logger.trace("Updating Steam app list...")
            app_count = 0
            try:
                apps = {
                    app.identifier: app
                    for app in await self.__api_client.get_app_list()
                }

                app_count = len(apps)
                self.__app_data = _AppData(
                    apps=apps,
                    suffix_tree=Tree({
                        app.identifier: app.name
                        for app in apps.values()
                    })
                )
            except Exception as error:
                self.__logger.error("Unexpected failure, updates will stop", error)
                raise
            finally:
                self.__logger.trace("Updated Steam app list", count=app_count)
            await wait(self.__options.value.RefreshResolution, token)
