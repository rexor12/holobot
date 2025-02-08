from collections.abc import Awaitable
from typing import Protocol

from PIL import Image, ImageFont

class IAssetManager(Protocol):
    def get_image(self, asset_id: str) -> Awaitable[Image.Image]:
        ...

    def get_font(self, asset_id: str, size: int) -> Awaitable[ImageFont.FreeTypeFont]:
        ...
