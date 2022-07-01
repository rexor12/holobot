from hikari import Embed as HikariEmbed
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter

def to_model(dto: HikariEmbed) -> Embed:
    embed = Embed(
        title=dto.title,
        description=dto.description,
        color=dto.color,
        thumbnail_url=dto.thumbnail.url if dto.thumbnail else None,
        image_url=dto.image.url if dto.image else None,
        footer = EmbedFooter(
            text=dto.footer.text,
            icon_url=dto.footer.icon.url if dto.footer.icon else None
        ) if dto.footer else None
    )

    for field in dto.fields:
        embed.fields.append(EmbedField(
            name=field.name, # type: ignore
            value=field.value, # type: ignore
            is_inline=field.inline # type: ignore
        ))

    return embed

def to_dto(model: Embed) -> HikariEmbed:
    dto = HikariEmbed(
        title=model.title,
        description=model.description,
        colour=model.color
    )

    if model.thumbnail_url:
        dto.set_thumbnail(model.thumbnail_url)
    elif model.image_url:
        dto.set_image(model.image_url)

    for field in model.fields:
        dto.add_field(
            name=field.name,
            value=field.value,
            inline=field.is_inline
        )

    if model.footer:
        dto.set_footer(
            text=model.footer.text,
            icon=model.footer.icon_url
        )

    return dto
