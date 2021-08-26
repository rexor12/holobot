from discord.embeds import Embed as DiscordEmbed, EmptyEmbed
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter

def remote_to_local(discord_embed: DiscordEmbed) -> Embed:
    embed = Embed(
        title=discord_embed.title,
        description=discord_embed.description,
        color=discord_embed.colour,
        thumbnail_url=discord_embed.thumbnail.url
    )

    for field in discord_embed.fields:
        embed.fields.append(EmbedField(
            name=field.name,
            value=field.value,
            is_inline=field.inline
        ))

    footer = discord_embed.footer
    if footer is not EmptyEmbed:
        text = footer.text if footer.text is not EmptyEmbed else None
        icon_url = footer.icon_url if footer.icon_url is not EmptyEmbed else None
        embed.footer = EmbedFooter(
            text=text,
            icon_url=icon_url
        )

    return embed

def local_to_remote(embed: Embed) -> DiscordEmbed:
    discord_embed = DiscordEmbed(
        title=embed.title,
        description=embed.description,
        colour=embed.color
    )

    if embed.thumbnail_url:
        discord_embed.set_thumbnail(url=embed.thumbnail_url)

    for field in embed.fields:
        discord_embed.add_field(
            name=field.name,
            value=field.value,
            inline=field.is_inline
        )

    if embed.footer:
        discord_embed.set_footer(
            text=embed.footer.text or EmptyEmbed,
            icon_url=embed.footer.icon_url or EmptyEmbed
        )

    return discord_embed
