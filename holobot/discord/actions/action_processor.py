from .iaction_processor import IActionProcessor
from discord.embeds import Embed as DiscordEmbed, EmptyEmbed
from discord_slash.context import MenuContext, SlashContext
from holobot.discord.sdk.actions import ActionBase, DoNothingAction, ReplyAction
from holobot.discord.sdk.models import Embed
from holobot.sdk.ioc.decorators import injectable
from typing import Union

@injectable(IActionProcessor)
class ActionProcessor(IActionProcessor):
    async def process(self, context: Union[MenuContext, SlashContext], action: ActionBase) -> None:
        if isinstance(action, DoNothingAction):
            return

        if isinstance(action, ReplyAction):
            if isinstance(action.content, Embed):
                await context.send(embed=ActionProcessor.__transform_embed(action.content))
            else: await context.send(action.content)
            return

    @staticmethod
    def __transform_embed(embed: Embed) -> DiscordEmbed:
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
