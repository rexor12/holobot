import io
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.extensions.general.repositories.user_profiles import IUserProfileBackgroundRepository
from holobot.sdk.diagnostics import Stopwatch
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.resources import IAssetManager
from .iuser_profile_factory import IUserProfileFactory

_BADGES_PER_ROW: int = 25
"""Defines the number of badge icons present in a single row of the badge_icons.png file."""

_BADGE_SIZE: int = 40
"""Defines the width and height of a badge icon."""

_BADGE_PADDING: int = 4
"""Defines the empty space between badges in the profile picture."""


_AVATAR_MASK = Image.new("L", (128, 128), 0)
_AVATAR_MASK_DRAWING_CONTEX = ImageDraw.Draw(_AVATAR_MASK)
_AVATAR_MASK_DRAWING_CONTEX.ellipse((0, 0, 128, 128), fill=255)

@dataclass(kw_only=True, frozen=True)
class _AssetCollection:
    card_background: Image.Image
    text_background: Image.Image
    badges_background: Image.Image
    progress_bar_background: Image.Image
    default_background: Image.Image
    avatar_border: Image.Image
    card_border: Image.Image
    reputation_icon: Image.Image
    default_avatar: Image.Image
    font_small: ImageFont.FreeTypeFont
    font_medium: ImageFont.FreeTypeFont
    font_large: ImageFont.FreeTypeFont
    badges: Image.Image

@injectable(IUserProfileFactory)
class UserProfileFactory(IUserProfileFactory):
    @property
    def priority(self) -> int:
        return 1000

    def __init__(
        self,
        asset_manager: IAssetManager,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reputation_data_provider: IReputationDataProvider,
        user_profile_background_repository: IUserProfileBackgroundRepository
    ) -> None:
        super().__init__()
        self.__assets = asset_manager
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(UserProfileFactory)
        self.__reputation_data_provider = reputation_data_provider
        self.__user_profile_background_repository = user_profile_background_repository

    async def create_profile_image(
        self,
        user_name: str,
        user_profile: UserProfile,
        avatar: bytes | None,
        custom_background_code: str | None = None
    ) -> bytes:
        background_code = (
            custom_background_code
            if custom_background_code
            else await self.__try_get_background_code(user_profile.background_image_id)
        )
        avatar_image = Image.open(io.BytesIO(avatar)) if avatar is not None else None
        user_profile_image = await self.__draw_user_profile_image(
            user_name,
            user_profile,
            avatar_image,
            await self.__get_background_image(background_code)
        )
        if avatar_image:
            avatar_image.close()

        output_bytes_io = io.BytesIO()
        user_profile_image.save(output_bytes_io, format="PNG")

        return output_bytes_io.getvalue()

    async def __try_get_background_code(
        self,
        background_id: int | None
    ) -> str | None:
        if not background_id:
            return None

        return await self.__user_profile_background_repository.get_code(background_id)

    async def __get_background_image(
        self,
        background_image_code: str | None
    ) -> Image.Image:
        if (
            not background_image_code
            or not (background_image := await self.__assets.get_image(
                f"images/user_profiles/custom_backgrounds/{background_image_code}.png"
            ))
        ):
            return await self.__assets.get_image(
                "images/user_profiles/default_background.png"
            )

        return background_image

    async def __get_or_load_assets(self) -> _AssetCollection:
        with Stopwatch(lambda e: self.__logger.trace("Loaded asset collection", elapsed=e)):
            return _AssetCollection(
                card_background=await self.__assets.get_image("images/user_profiles/card_background.png"),
                text_background=await self.__assets.get_image("images/user_profiles/text_background.png"),
                badges_background=await self.__assets.get_image("images/user_profiles/badges.png"),
                progress_bar_background=await self.__assets.get_image("images/user_profiles/progress_bar_background.png"),
                default_background=await self.__assets.get_image("images/user_profiles/default_background.png"),
                avatar_border=await self.__assets.get_image("images/user_profiles/avatar_border_default.png"),
                card_border=await self.__assets.get_image("images/user_profiles/card_border.png"),
                reputation_icon=await self.__assets.get_image("images/user_profiles/reputation_icon.png"),
                default_avatar=await self.__assets.get_image("images/user_profiles/default_avatar.png"),
                font_small=await self.__assets.get_font("fonts/AGPmod.ttf", 15),
                font_medium=await self.__assets.get_font("fonts/AGPmod.ttf", 20),
                font_large=await self.__assets.get_font("fonts/AGPmod.ttf", 30),
                badges=await self.__assets.get_image("images/user_profiles/badge_icons.png")
            )

    async def __draw_user_profile_image(
        self,
        username: str,
        user_profile: UserProfile,
        avatar: Image.Image | None,
        background_image: Image.Image
    ) -> Image.Image:
        reputation_points = user_profile.reputation_points
        rank_info = self.__reputation_data_provider.get_rank_info(reputation_points)
        title = self.__i18n.get_list_item("extensions.general.user_profile_titles", rank_info.current_rank)
        if avatar is None:
            avatar = await self.__assets.get_image(
                "images/user_profiles/default_avatar.png"
            )
        else:
            avatar = avatar.resize((128, 128), Image.Resampling.LANCZOS)

        assets = await self.__get_or_load_assets()
        avatar_cropped = Image.new("RGBA", avatar.size, (255, 255, 255, 0))
        avatar_cropped.paste(avatar, mask=_AVATAR_MASK)

        profile_image = Image.new("RGBA", (548, 174), None)
        profile_image.paste(assets.card_background)
        profile_image.paste(background_image, background_image)
        profile_image.paste(avatar_cropped, (23, 23), avatar_cropped)
        profile_image.paste(assets.avatar_border, (22, 22), assets.avatar_border)
        profile_image.paste(assets.text_background, mask=assets.text_background)
        profile_image.paste(assets.reputation_icon, (192, 81), assets.reputation_icon)
        self.__draw_badges(profile_image, user_profile, assets)
        profile_image.paste(assets.card_border, mask=assets.card_border)

        drawing_context = ImageDraw.Draw(profile_image)
        drawing_context.text(xy=(195, 20), text=username[:20], font=assets.font_large, fill=(102, 102, 102), stroke_width=1, stroke_fill="black")
        drawing_context.text(xy=(194, 56), text=title, font=assets.font_medium, fill="black")
        drawing_context.text(xy=(193, 55), text=title, font=assets.font_medium, fill=rank_info.color)

        if reputation_points < 100_000:
            reputation_bar_scale = min(1, (reputation_points - rank_info.last_required) / (rank_info.next_required - rank_info.last_required))
            reputation_bar_width = int(307 * reputation_bar_scale)
            profile_image.paste(assets.progress_bar_background, (220, 85))
            if reputation_bar_width > 0:
                drawing_context.rectangle(((220, 85), (220 + reputation_bar_width, 99)), fill=rank_info.color)
            drawing_context.text(xy=(366, 92), text=f"{reputation_points}/{rank_info.next_required}", anchor="mm", align="center", font=assets.font_small, fill="white", stroke_width=1, stroke_fill="black")
        else:
            drawing_context.text(xy=(220, 80), text=f"{reputation_points}", font=assets.font_medium, fill=(91, 7, 7), stroke_width=1, stroke_fill="black")

        return profile_image

    def __draw_badges(
        self,
        profile_image: Image.Image,
        user_profile: UserProfile,
        assets: _AssetCollection
    ) -> None:
        if not user_profile.show_badges:
            return

        profile_image.paste(assets.badges_background, mask=assets.badges_background)
        for badge_index, badge_id in enumerate(user_profile.badges):
            if not badge_id:
                continue

            badge_x = (badge_id.badge_id % _BADGES_PER_ROW) * _BADGE_SIZE
            badge_y = (badge_id.badge_id // _BADGES_PER_ROW) * _BADGE_SIZE
            badge_icon = assets.badges.crop(
                (badge_x, badge_y, badge_x + _BADGE_SIZE, badge_y + _BADGE_SIZE)
            )
            target_position = (badge_index * (_BADGE_SIZE + _BADGE_PADDING) + 183, 120)
            profile_image.paste(badge_icon, target_position, badge_icon)
