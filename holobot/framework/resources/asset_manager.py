import os
from collections.abc import Awaitable
from datetime import timedelta
from typing import Generic, Protocol, TypeVar

from PIL import Image, ImageFont

from holobot.framework.configs import EnvironmentOptions
from holobot.sdk import IDisposable
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILogger, ILoggerFactory
from holobot.sdk.resources import IAssetManager
from holobot.sdk.system import IEnvironment
from holobot.sdk.threading.utils import as_task

class _IClosable(Protocol):
    def close(self) -> None:
        ...

TClosable = TypeVar("TClosable", bound=_IClosable)

class _DisposableAsset(IDisposable, Generic[TClosable]):
    @property
    def asset(self) -> TClosable:
        return self.__asset

    def __init__(
        self,
        asset_id: str,
        asset: TClosable,
        logger: ILogger
    ) -> None:
        super().__init__()
        self.__asset_id = asset_id
        self.__asset = asset
        self.__logger = logger

    def _on_dispose(self) -> None:
        self.__asset.close()
        self.__logger.trace("Disposed asset", asset_id=self.__asset_id)

@injectable(IAssetManager)
class AssetManager(IAssetManager):
    def __init__(
        self,
        cache: IObjectCache,
        environment: IEnvironment,
        logger_factory: ILoggerFactory,
        options: IOptions[EnvironmentOptions]
    ) -> None:
        self.__cache = cache
        self.__environment = environment
        self.__logger = logger_factory.create(AssetManager)
        self.__options = options
        self.__asset_expiration_time = timedelta(
            minutes=options.value.AssetSlidingExpirationTimeInMinutes
        )

    async def get_image(self, asset_id: str) -> Image.Image:
        cache_key = AssetManager.__get_cache_key("image", asset_id)
        asset = await self.__cache.get_or_add(
            cache_key,
            lambda _: self.__load_image(asset_id),
            SlidingExpirationCacheEntryPolicy(self.__asset_expiration_time)
        )
        if not isinstance(asset, _DisposableAsset) or not isinstance(asset.asset, Image.Image):
            raise ValueError(f"The already loaded asset with identifier '{asset_id}' is not an image.")

        return asset.asset

    async def get_font(self, asset_id: str, size: int) -> ImageFont.FreeTypeFont:
        cache_key = AssetManager.__get_cache_key(f"font-{size}", asset_id)
        asset = await self.__cache.get_or_add(
            cache_key,
            lambda _: self.__load_font(asset_id, size),
            SlidingExpirationCacheEntryPolicy(self.__asset_expiration_time)
        )
        if not isinstance(asset, ImageFont.FreeTypeFont):
            raise ValueError(f"The already loaded asset with identifier '{asset_id}' is not a font.")

        return asset

    @staticmethod
    def __get_cache_key(asset_type: str, asset_id: str) -> str:
        return f"asset/{asset_type}/{asset_id}"

    def __get_asset_path(self, asset_id: str) -> str:
        if not self.__options.value.ResourceDirectoryPaths:
            return os.path.join(self.__environment.root_path, asset_id)

        for resource_directory_path in self.__options.value.ResourceDirectoryPaths:
            resource_path = os.path.join(resource_directory_path, asset_id)
            if os.path.exists(resource_path):
                return resource_path

        raise FileNotFoundError(f"Asset with identifier '{asset_id}' cannot be found.")

    def __load_image(self, asset_id: str) -> Awaitable[_DisposableAsset[Image.Image]]:
        asset_path = self.__get_asset_path(asset_id)
        asset = Image.open(asset_path)

        self.__logger.trace("Loaded image asset", path=asset_path)

        return as_task(_DisposableAsset[Image.Image](
            asset_path,
            asset,
            self.__logger
        ))

    def __load_font(self, asset_id: str, size: int) -> Awaitable[ImageFont.FreeTypeFont]:
        asset_path = self.__get_asset_path(asset_id)
        asset = ImageFont.truetype(asset_path, size=size)

        self.__logger.trace("Loaded font asset", path=asset_path)

        return as_task(asset)
