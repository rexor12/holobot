import discord.ext.commands as commands

class IBotEventHandler:
    def register_callbacks(self, bot: commands.Bot) -> None:
        raise NotImplementedError
