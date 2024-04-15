import io
import os
import re
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.extensions.general.options import UserProfileOptions
from holobot.extensions.general.providers import IReputationDataProvider
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.system import IEnvironment
from .iuser_profile_factory import IUserProfileFactory

_IMAGE_FILE_NAME_REGEX = re.compile(r"^(?P<name>\w+)\.(png|jpg)$", re.IGNORECASE)

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
    custom_backgrounds: dict[str, Image.Image] = field(default_factory=dict)

@injectable(IUserProfileFactory)
class UserProfileFactory(IUserProfileFactory):
    def __init__(
        self,
        environment: IEnvironment,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        options: IOptions[UserProfileOptions],
        reputation_data_provider: IReputationDataProvider
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__logger = logger_factory.create(UserProfileFactory)
        self.__reputation_data_provider = reputation_data_provider
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
            font_small=self.__load_font(environment, "AGPmod.ttf", 15),
            font_medium=self.__load_font(environment, "AGPmod.ttf", 20),
            font_large=self.__load_font(environment, "AGPmod.ttf", 30),
            custom_backgrounds=self.__load_custom_backgrounds(environment, options.value.CustomBackgroundsPath)
        )

    def create_profile_image(
        self,
        user_name: str,
        user_profile: UserProfile,
        avatar: bytes | None,
        custom_background_code: str | None = None
    ) -> bytes:
        user_profile_image = self.__draw_user_profile_image(
            user_name,
            user_profile.reputation_points,
            Image.open(io.BytesIO(avatar)) if avatar is not None else None,
            self.__get_background_image(custom_background_code or user_profile.background_image_code)
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

    def __load_custom_backgrounds(
        self,
        environment: IEnvironment,
        relative_path: str
    ) -> dict[str, Image.Image]:
        custom_backgrounds = dict[str, Image.Image]()
        directory_path = os.path.join(environment.root_path, relative_path)
        for custom_background in self.__reputation_data_provider.get_custom_backgrounds():
            asset_path = os.path.join(directory_path, custom_background.file_name)
            if not os.path.isfile(asset_path):
                continue

            self.__logger.debug("Loading custom background...", path=asset_path)
            custom_backgrounds[custom_background.code] = Image.open(asset_path)

        return custom_backgrounds

    def __get_background_image(
        self,
        background_image_code: str | None
    ) -> Image.Image:
        if not background_image_code:
            return self.__assets.default_background

        if background_image := self.__assets.custom_backgrounds.get(background_image_code, None):
            return background_image

        return self.__assets.default_background

    def __draw_user_profile_image(
        self,
        username: str,
        reputation_points: int,
        avatar: Image.Image | None,
        background_image: Image.Image
    ) -> Image.Image:
        rank_info = self.__reputation_data_provider.get_rank_info(reputation_points)
        title = self.__i18n.get_list_item("extensions.general.user_profile_titles", rank_info.current_rank)
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
        profile_image.paste(self.__assets.card_background)
        profile_image.paste(background_image, background_image)
        profile_image.paste(avatar_cropped, (23, 23), avatar_cropped)
        profile_image.paste(self.__assets.avatar_border, (22, 22), self.__assets.avatar_border)
        profile_image.paste(self.__assets.text_background, mask=self.__assets.text_background)
        profile_image.paste(self.__assets.reputation_icon, (192, 81), self.__assets.reputation_icon)
        # profile_image.paste(self.__assets.badges_background, mask=self.__assets.badges_background)
        profile_image.paste(self.__assets.card_border, mask=self.__assets.card_border)

        drawing_context = ImageDraw.Draw(profile_image)
        drawing_context.text(xy=(195, 20), text=username[:20], font=self.__assets.font_large, fill=(102, 102, 102), stroke_width=1, stroke_fill="black")
        drawing_context.text(xy=(194, 56), text=title, font=self.__assets.font_medium, fill="black")
        drawing_context.text(xy=(193, 55), text=title, font=self.__assets.font_medium, fill=rank_info.color)

        if reputation_points < 100_000:
            reputation_bar_scale = min(1, (reputation_points - rank_info.last_required) / (rank_info.next_required - rank_info.last_required))
            reputation_bar_width = int(240 * reputation_bar_scale)
            profile_image.paste(self.__assets.progress_bar_background, (220, 85))
            if reputation_bar_width > 0:
                drawing_context.rectangle(((220, 85), (220 + reputation_bar_width, 99)), fill=rank_info.color)
            drawing_context.text(xy=(366, 92), text=f"{reputation_points}/{rank_info.next_required}", anchor="mm", align="center", font=self.__assets.font_small, fill="white", stroke_width=1, stroke_fill="black")
        else:
            drawing_context.text(xy=(220, 80), text=f"{reputation_points}", font=self.__assets.font_medium, fill=(91, 7, 7), stroke_width=1, stroke_fill="black")

        return profile_image
