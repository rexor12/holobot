import io
import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment
from .iuser_profile_factory import IUserProfileFactory

_REP_RANKS: tuple[tuple[int, tuple[int, int, int]], ...] = (
    (0,          (157, 157, 157)),
    (50,         (157, 157, 157)),
    (100,        (157, 157, 157)),

    (200,        (255, 255, 255)),
    (350,        (255, 255, 255)),
    (500,        (255, 255, 255)),

    (750,        (30, 255, 0)),
    (1000,       (30, 255, 0)),
    (1500,       (30, 255, 0)),

    (2000,       (0, 112, 221)),
    (4000,       (0, 112, 221)),
    (6000,       (0, 112, 221)),

    (8000,       (163, 53, 238)),
    (10000,      (163, 53, 238)),
    (15000,      (163, 53, 238)),

    (30000,      (255, 128, 0)),
    (50000,      (255, 128, 0)),
    (75000,      (255, 128, 0)),

    (100000,     (230, 204, 128))
)

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
    font_medium: ImageFont.FreeTypeFont
    font_large: ImageFont.FreeTypeFont

@injectable(IUserProfileFactory)
class UserProfileFactory(IUserProfileFactory):
    def __init__(
        self,
        environment: IEnvironment,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__assets = _AssetCollection(
            card_background=self.__load_image(environment, "card_background.png"),
            text_background=self.__load_image(environment, "text_background.png"),
            badges_background=self.__load_image(environment, "badges.png"),
            progress_bar_background=self.__load_image(environment, "progress_bar_background.png"),
            default_background=self.__load_image(environment, "default_background.png"),
            avatar_border=self.__load_image(environment, "avatar_border_default.png"),
            card_border=self.__load_image(environment, "card_border.png"),
            reputation_icon=self.__load_image(environment, "reputation_icon.png"),
            default_avatar=self.__load_image(environment, "default_avatar.png"),
            font_medium=self.__load_font(environment, "AGPmod.ttf", 20),
            font_large=self.__load_font(environment, "AGPmod.ttf", 30)
        )

    def create_profile_image(
        self,
        user_name: str,
        user_profile: UserProfile,
        avatar: bytes | None
    ) -> bytes:
        user_profile_image = self.__draw_user_profile_image(
            user_name,
            user_profile.reputation_points,
            Image.open(io.BytesIO(avatar)) if avatar is not None else None
        )
        output_bytes_io = io.BytesIO()
        user_profile_image.save(output_bytes_io, format="PNG")

        return output_bytes_io.getvalue()

    @staticmethod
    def __load_image(environment: IEnvironment, asset_name: str) -> Image.Image:
        asset_path = os.path.join(environment.root_path, "resources/images/user_profiles", asset_name)
        return Image.open(asset_path)

    @staticmethod
    def __load_font(environment: IEnvironment, asset_name: str, size: int) -> ImageFont.FreeTypeFont:
        asset_path = os.path.join(environment.root_path, "resources/fonts", asset_name)
        return ImageFont.truetype(asset_path, size=size)

    @staticmethod
    def __get_rep_info(reputation_points: int) -> tuple[int, int, int]:
        # Binary search to find the current rank.
        left, right = 0, len(_REP_RANKS) - 1
        current_rank = 0
        while left <= right:
            mid = left + (right - left) // 2
            if _REP_RANKS[mid][0] <= reputation_points:
                current_rank = mid
                left = mid + 1
            else:
                right = mid - 1

        return (
            current_rank,
            1 if current_rank >= len(_REP_RANKS) - 1 else _REP_RANKS[current_rank + 1][0],
            0 if current_rank <= 0 else _REP_RANKS[current_rank - 1][0]
        )

    def __draw_user_profile_image(
        self,
        username: str,
        reputation_points: int,
        avatar: Image.Image | None
    ) -> Image.Image:
        rep_rank, next_rep, last_rep = UserProfileFactory.__get_rep_info(reputation_points)
        title = self.__i18n.get_list_item("extensions.general.user_profile_titles", rep_rank)
        title_color = _REP_RANKS[rep_rank][1]
        if avatar is None:
            avatar = self.__assets.default_avatar
        else:
            avatar = avatar.resize((128, 128), Image.Resampling.LANCZOS)

        avatar_mask = Image.new("L", (128, 128), 0)
        avatar_mask_drawing_context = ImageDraw.Draw(avatar_mask)
        avatar_mask_drawing_context.ellipse((0, 0, 128, 128), fill=255)
        avatar_cropped = Image.new("RGBA", avatar.size, (255, 255, 255, 0))
        avatar_cropped.paste(avatar, mask=avatar_mask)

        profile_image = Image.new("RGBA", (548, 174), None)
        profile_image.paste(self.__assets.card_background, mask=self.__assets.card_background)
        profile_image.paste(self.__assets.default_background, mask=self.__assets.default_background)
        profile_image.paste(avatar_cropped, (23, 23), avatar_cropped)
        profile_image.paste(self.__assets.avatar_border, (22, 22), self.__assets.avatar_border)
        profile_image.paste(self.__assets.text_background, mask=self.__assets.text_background)
        profile_image.paste(self.__assets.reputation_icon, (192, 81), self.__assets.reputation_icon)
        # profile_image.paste(self.__assets.badges_background, mask=self.__assets.badges_background)
        profile_image.paste(self.__assets.card_border, mask=self.__assets.card_border)

        drawing_context = ImageDraw.Draw(profile_image)
        drawing_context.text(xy=(195, 20), text=username[:20], font=self.__assets.font_large, fill=(102, 102, 102), stroke_width=1, stroke_fill="black")
        drawing_context.text(xy=(194, 56), text=title, font=self.__assets.font_medium, fill="black")
        drawing_context.text(xy=(193, 55), text=title, font=self.__assets.font_medium, fill=title_color)

        if reputation_points < 100_000:
            reputation_bar_scale = min(1, (reputation_points - last_rep) / (next_rep - last_rep))
            reputation_bar_width = int(240 * reputation_bar_scale)
            profile_image.paste(self.__assets.progress_bar_background, (220, 85))
            drawing_context.text(xy=(465, 80), text=f"{reputation_points}", font=self.__assets.font_medium, fill=(89, 3, 3), stroke_width=1, stroke_fill="black")
            if reputation_bar_width > 0:
                drawing_context.rectangle(((220, 85), (220 + reputation_bar_width, 99)), fill=title_color)
        else:
            drawing_context.text(xy=(220, 80), text=f"{reputation_points}", font=self.__assets.font_medium, fill=(89, 3, 3), stroke_width=1, stroke_fill="black")

        return profile_image
