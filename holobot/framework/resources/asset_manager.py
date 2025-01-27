import os
from datetime import timedelta

from PIL import Image, ImageFont

from holobot.framework.configs import EnvironmentOptions
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.resources import IAssetManager
from holobot.sdk.system import IEnvironment

_ASSET_EXPIRATION_TIME = timedelta(minutes=10) # TODO Config

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

    async def get_image(self, asset_id: str) -> Image.Image:
        cache_key = AssetManager.__get_cache_key("image", asset_id)
        asset = await self.__cache.get_or_add(
            cache_key,
            lambda: self.__load_image(asset_id),
            SlidingExpirationCacheEntryPolicy(_ASSET_EXPIRATION_TIME)
        )
        if not isinstance(asset, Image.Image):
            raise ValueError(f"The already loaded asset with identifier '{asset_id}' is not an image.")

        return asset

    async def get_font(self, asset_id: str, size: int) -> ImageFont.FreeTypeFont:
        cache_key = AssetManager.__get_cache_key(f"font-{size}", asset_id)
        asset = await self.__cache.get_or_add(
            cache_key,
            lambda: self.__load_font(asset_id, size),
            SlidingExpirationCacheEntryPolicy(_ASSET_EXPIRATION_TIME)
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

    def __load_image(self, asset_id: str) -> Image.Image:
        asset_path = self.__get_asset_path(asset_id)
        return Image.open(asset_path)

    def __load_font(self, asset_id: str, size: int) -> ImageFont.FreeTypeFont:
        asset_path = self.__get_asset_path(asset_id)
        return ImageFont.truetype(asset_path, size=size)
